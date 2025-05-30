#!/usr/bin/env python3
import os, time, threading, random, logging
from prometheus_client import start_http_server, Gauge
from qiskit import QuantumCircuit, Aer, execute
from scapy.all import IP, UDP, Raw, send

# Metrics
qber = Gauge('bb84_qber', 'Quantum bit error rate')
keyrate = Gauge('bb84_key_rate', 'Raw key rate (bits/sec)')

# UDP target
dst_ip   = os.getenv('QKD_DST_IP')
dst_port = int(os.getenv('QKD_DST_PORT'))

logging.basicConfig(level=logging.INFO)

def send_udp(payload: bytes):
    pkt = IP(dst=dst_ip)/UDP(dport=dst_port)/Raw(load=payload)
    send(pkt, verbose=False)
    logging.debug(f"Sent BB84 UDP → {dst_ip}:{dst_port}")

def simulate_bb84():
    backend = Aer.get_backend('aer_simulator')
    N = 64
    bits  = [random.randint(0,1) for _ in range(N)]
    bases = [random.choice([0,1]) for _ in range(N)]
    measured=[]
    for b,base in zip(bits,bases):
        qc = QuantumCircuit(1,1)
        if b: qc.x(0)
        if base: qc.h(0)
        qc.measure(0,0)
        res = list(execute(qc,backend,shots=1).result().get_counts().keys())[0]
        measured.append(int(res))
    errors = sum(x!=y for x,y in zip(bits,measured))/N
    qber.set(errors); keyrate.set(N/5)
    summary = f"BB84 QBER={errors:.4f}, rate={N/5:.1f}".encode()
    send_udp(summary)
    logging.info(f"[BB84] QBER={errors:.2%}")

def loop():
    while True:
        simulate_bb84()
        time.sleep(10)

if __name__=="__main__":
    start_http_server(int(os.getenv('METRICS_PORT')))
    threading.Thread(target=loop,daemon=True).start()
    while True:
        time.sleep(60)
# This code simulates a BB84 quantum key distribution protocol using Qiskit and sends metrics via UDP.
# It generates random bits and bases, simulates quantum measurements, calculates the quantum bit error rate (QBER),
# and sends the results to a specified destination IP and port. It also exposes metrics via Prometheus.
# The simulation runs in a loop, updating the metrics every 10 seconds.
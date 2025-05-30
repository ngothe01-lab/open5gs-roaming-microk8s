#!/usr/bin/env python3
import os, time, threading, random, logging
from prometheus_client import start_http_server, Gauge
from bitstring import BitArray
from scapy.all import IP, UDP, Raw, send

# Metrics
throughput = Gauge('dl04_throughput','DL04 throughput (bps)')
integrity = Gauge('dl04_integrity_ok','Fraction of correctly received bits')

# UDP target
dst_ip   = os.getenv('QSDC_DST_IP')
dst_port = int(os.getenv('QSDC_DST_PORT'))

logging.basicConfig(level=logging.INFO)

def send_udp(payload: bytes):
    pkt = IP(dst=dst_ip)/UDP(dport=dst_port)/Raw(load=payload)
    send(pkt, verbose=False)
    logging.debug(f"Sent DL04 UDP → {dst_ip}:{dst_port}")

def simulate_dl04():
    L = 128
    bits  = BitArray(uint=random.getrandbits(L), length=L)
    noisy = BitArray(bits)
    for i in range(L):
        if random.random()<0.01: noisy.invert(i)
    corr = sum(bits[i]==noisy[i] for i in range(L))/L
    throughput.set(L/5); integrity.set(corr)
    summary = f"DL04 integrity={corr:.4f}, len={L}".encode()
    send_udp(summary)
    logging.info(f"[DL04] Integrity={corr:.2%}")

def loop():
    while True:
        simulate_dl04()
        time.sleep(12)

if __name__=="__main__":
    start_http_server(int(os.getenv('METRICS_PORT')))
    threading.Thread(target=loop,daemon=True).start()
    while True:
        time.sleep(60)
# This code simulates a DL04 quantum secure data communication protocol.
# It generates random bits, simulates noisy transmission, calculates the integrity of the received bits,
# and sends the results via UDP to a specified destination IP and port.
# It also exposes metrics via Prometheus, including throughput and integrity.
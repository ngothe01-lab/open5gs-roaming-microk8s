# ipx-only/Dockerfile
FROM python:3.10-slim

LABEL maintainer="TJ Ngobeni"

ENV DEBIAN_FRONTEND=noninteractive \
    BRIDGE=br0 \
    OF_VERSION=OpenFlow13 \
    CONTROLLER_ADDR=127.0.0.1:6633 \
    METRICS_PORT=8000 \
    QKD_DST_IP=127.0.0.1 \
    QKD_DST_PORT=4000 \
    QSDC_DST_IP=127.0.0.1 \
    QSDC_DST_PORT=5000

# 1) Install OVS (OpenFlow) and cleanup
RUN apt-get update \
 && apt-get install -y --no-install-recommends openvswitch-switch \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copy & install Python dependencies
COPY requirements-common.txt requirements-qkd.txt requirements-qsd.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements-common.txt \
 && pip install --no-cache-dir -r requirements-qkd.txt \
 && pip install --no-cache-dir -r requirements-qsd.txt

# 3) Copy entrypoint and controller scripts
COPY combined-entrypoint.sh qkd_controller.py qsd_controller.py ./
RUN chmod +x combined-entrypoint.sh qkd_controller.py qsd_controller.py

# 4) Expose OpenFlow & metrics ports
# OVS/OpenFlow # Prometheus metrics
EXPOSE 6633  
EXPOSE 8000  

# 5) Healthcheck for OVS bridge
HEALTHCHECK --interval=30s --timeout=5s CMD ovs-vsctl show || exit 1

# 6) Launch OVS + controllers
ENTRYPOINT ["./combined-entrypoint.sh"]

#!/usr/bin/env bash
set -euo pipefail

# 1) Start OVS control plane
ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock --detach
ovs-vswitchd --detach

# 2) Configure bridge
ovs-vsctl add-br "$BRIDGE"
ovs-vsctl set bridge "$BRIDGE" protocols="$OF_VERSION"
ovs-vsctl set-controller "$BRIDGE" tcp:"$CONTROLLER_ADDR"

# 3) Launch BB84 (QKD) simulator
python3 qkd_controller.py &

# 4) Launch DL04 (QSDC) simulator
python3 qsd_controller.py &

# 5) Keep container alive
wait -n
exit $?
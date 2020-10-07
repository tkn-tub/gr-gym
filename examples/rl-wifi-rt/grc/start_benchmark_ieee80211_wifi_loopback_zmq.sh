#!/bin/bash

if [ "$1" == "" ] || [ $# -gt 1 ]; then
    echo "Please set name of remote node"
fi

remote_addr=$1

echo "Creating GRC to $remote_addr"

sed -i 's/localhost/$remote_addr/g' benchmark_ieee80211_wifi_loopback_zmq_remote.grc > tmp.grc
grcc tmp.grc
python3 tmp.py > /tmp/out.log 2>&1

#!/bin/bash

if [ "$1" == "" ] || [ $# -gt 1 ]; then
    echo "Please set name of remote node"
    exit 1
fi

remote_addr=$1

echo "Creating GRC to $remote_addr"

cat benchmark_ieee80211_wifi_loopback_zmq_remote.grc | sed "s/localhost/$remote_addr/g" > tmp.grc
grcc tmp.grc
python3 benchmark_ieee80211_wifi_loopback_zmq.py > /tmp/out.log 2>&1

#!/bin/bash

grcc simple_benchmark.grc
python3 simple_benchmark.py > /tmp/out.log 2>&1

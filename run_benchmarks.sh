#!/bin/bash

quilc -S &
qvm -c -O 3 -S &
qubit-toaster -S &

sleep 1s

python3 ./benchmark_qft.py

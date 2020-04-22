quilc -S & # > /dev/null 2>&1 &
qvm -c -O 3 -S & # > /dev/null 2>&1 &
qubit-toaster -S & # > /dev/null 2>&1 &

sleep 1s

python /root/benchmark_qft.py

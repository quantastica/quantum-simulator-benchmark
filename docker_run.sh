#!/bin/bash

docker run -it --name quantum-benchmark -v $(pwd)/output/:/root/output/ quantastica/quantum-benchmark
docker rm quantum-benchmark


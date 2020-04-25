#!/bin/bash

docker run -it --rm --name quantum-benchmark -v $(pwd)/output/:/root/output/ quantastica/quantum-benchmark


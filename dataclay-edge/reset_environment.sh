#!/bin/bash
set -e
set -x

./stop_all_containers.sh
./deploy_all_cuda_containers.sh down
./deploy_all_cuda_containers.sh up
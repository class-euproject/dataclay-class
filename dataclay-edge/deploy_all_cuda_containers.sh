#!/bin/bash
set -e
set -x

# Fog node 1
CAM_IDS_1=(20936 20937 20939 10218)
TKDNN_PORTS_1=(5560 5561 5562 5563)

ssh -t esabate@192.168.7.32 "ssh bsc@192.168.12.1 'cd dataclay-class/ && git pull && cd dataclay-edge/ && CAM_IDS=(${CAM_IDS_1[@]}) TKDNN_PORTS=(${TKDNN_PORTS_1[@]}) ./deploy_cuda_containers.sh $1'"

# Fog node 2
CAM_IDS_2=(20940 20932 637 6310 634)
TKDNN_PORTS_2=(5560 5561 5562 5563 5564)

ssh -t esabate@192.168.7.32 "ssh bsc@192.168.12.2 'cd dataclay-class/ && git pull && cd dataclay-edge/ && CAM_IDS=(${CAM_IDS_2[@]}) TKDNN_PORTS=(${TKDNN_PORTS_2[@]}) ./deploy_cuda_containers.sh $1'"

# Fog node 3
CAM_IDS_3=(6314 6313 6312 6311 636 6315)
TKDNN_PORTS_3=(5560 5561 5562 5563 5564 5565)

ssh -t esabate@192.168.7.32 "ssh bsc@192.168.12.3 'cd dataclay-class/ && git pull && cd dataclay-edge/ && CAM_IDS=(${CAM_IDS_3[@]}) TKDNN_PORTS=(${TKDNN_PORTS_3[@]}) ./deploy_cuda_containers.sh $1'"
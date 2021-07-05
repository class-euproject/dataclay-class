#!/bin/bash
set -e
set -x

bkpIFS="$IFS"

IFS='( )' read -r -a CAM_IDS_ARR <<<${CAM_IDS}
IFS='( )' read -r -a TKDNN_PORTS_ARR <<<${TKDNN_PORTS}

IFS="$bkpIFS"

function deploy_all_cuda_containers {

	if [[ $1 = "up" ]]
	then

		for ((i=1; i<${#CAM_IDS_ARR[@]}; i++));
		do
			CAM_ID=${CAM_IDS_ARR[$i]} TKDNN_PORT=${TKDNN_PORTS_ARR[$i]} docker-compose -f docker-compose-cuda.yml up -d --no-recreate --scale object-detection=$((i));
		done

	else
		CAM_ID=99999 TKDNN_PORT=99999 docker-compose -f docker-compose-cuda.yml down
	fi

}

deploy_all_cuda_containers $1
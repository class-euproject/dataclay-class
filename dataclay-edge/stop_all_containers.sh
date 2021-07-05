#!/bin/bash
set -e

main_server_ip=192.168.7.32
main_server_user=esabate
fog_node_user=bsc

declare -a fog_nodes=('192.168.12.1' '192.168.12.2' '192.168.12.3' '192.168.12.4')

for ip in ${fog_nodes[@]}
do
	#ssh ${main_server_user}@${main_server_ip} "ssh ${fog_node_user}@${ip} 'docker container ls -a | awk "'"{print \$NF}"'" | grep tracking_partial | xargs -r docker container stop'"
	ssh ${main_server_user}@${main_server_ip} "ssh ${fog_node_user}@${ip} 'docker container ls -a | awk "'"{print \$NF}"'" | grep class-object-tracking | xargs -r docker container rm -f'"
done

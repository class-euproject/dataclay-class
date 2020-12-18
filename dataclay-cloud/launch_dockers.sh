#!/bin/bash

echo "Removing old dockers"
docker-compose kill && docker-compose down -v

echo "Launching dockers again"
docker-compose up --build -d # launches also the docker that contains the 
			     # stubs, creates the DKB and retrieves the objects 
			     # send through federeation

# check if dockers already up and registered
res=$(docker-compose logs 2>&1 | grep " ===> The ContractID for the registered classes is:")
# while [ ! $(docker-compose logs 2>&1 | grep -q " ===> The ContractID for the registered classes is:") ];
while [ -z $res ];
do
        echo "Dataclay initializer not ready yet. Waiting for it to finish..."
        sleep 3
        res=$(docker-compose logs 2>&1 | grep " ===> The ContractID for the registered classes is:")
done
echo "Dataclay initializer registered model, stubs can be retrieved."

# to run the simulator, debug, or whatever			     
./GetStubs.sh


#!/bin/bash
export COMMAND_OPTS="--debug"

echo "** Removing existing dockers **"
docker-compose -f dataclay/docker-compose.yml kill 
docker-compose -f dataclay/docker-compose.yml down -v

echo "** Deploying dockers **"
docker-compose -f dataclay/docker-compose.yml pull 
docker-compose -f dataclay/docker-compose.yml up -d

echo "** Wait for dataClay to be alive **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles --network dataclay_default bscdataclay/client:2.4.dev WaitForDataClayToBeAlive 10 5

echo "** Getting stubs from dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles -v $PWD/stubs:/stubs --network dataclay_default bscdataclay/client:2.4.dev GetStubs CityUser p4ssw0rd CityNS /stubs

cd app
python3.7 create_dkb.py

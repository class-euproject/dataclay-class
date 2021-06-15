#!/bin/bash

rm -rf /compss/stubs 

docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles       \
           -v /compss/stubs:/stubs --network host -e HOST_USER_ID=$(id -u) \
           -e HOST_GROUP_ID=$(id -g) bscdataclay/client:dev20210603-alpine \
           GetStubs CityUser p4ssw0rd CityNS /stubs

rm /compss/dataclay.jar
ID=$(docker create bscdataclay/logicmodule:dev20210603-alpine)
docker cp $ID:/home/dataclayusr/dataclay/dataclay.jar /compss
docker rm $ID

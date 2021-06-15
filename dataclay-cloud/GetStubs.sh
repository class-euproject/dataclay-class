#!/bin/bash

rm -rf $PWD/stubs

docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles       \
           -v $PWD/stubs:/stubs --network host -e HOST_USER_ID=$(id -u)    \
           -e HOST_GROUP_ID=$(id -g) bscdataclay/client:dev20210603-alpine \
	   GetStubs CityUser p4ssw0rd CityNS /stubs


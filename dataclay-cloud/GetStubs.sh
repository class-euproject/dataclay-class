#!/bin/bash

sudo rm -rf $PWD/stubs

docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
           -v $PWD/stubs:/stubs --network host \
           bscdataclay/client:dev20210428-alpine GetStubs CityUser p4ssw0rd CityNS /stubs


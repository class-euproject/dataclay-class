#!/bin/bash

docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
           -v $PWD/stubs:/stubs --network host \
           bscdataclay/client:alpine GetStubs CityUser p4ssw0rd CityNS /stubs


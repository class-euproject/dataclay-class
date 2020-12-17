#!/bin/bash

echo "Removing old dockers"
docker-compose kill && docker-compose down -v

echo "Launching dockers again"
docker-compose up --build -d # launches also the docker that contains the 
			     # stubs, creates the DKB and retrieves the objects 
			     # send through federeation



#!/bin/bash

#=== FUNCTION ================================================================
# NAME: deploy
# DESCRIPTION: Deploy to DockerHub and retry if connection fails
#=============================================================================
function deploy {
  echo "$@"
  export n=0
  until [ "$n" -ge 5 ] # Retry maximum 5 times
  do
    eval "$@" && break
    n=$((n+1))
    sleep 15
  done
}
#=


export COMMAND_OPTS="" # to debug put "--debug" here

echo "** Removing existing dockers **"
docker-compose -f dataclay/docker-compose.yml kill
docker-compose -f dataclay/docker-compose.yml down -v

echo "** Deploying dockers **"
docker-compose -f dataclay/docker-compose.yml up -d

echo "** Wait for dataClay to be alive **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
	   --network dataclay_default bscdataclay/client:2.5.dev     \
	   WaitForDataClayToBeAlive 10 5

echo "** Registering new account in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
	   --network dataclay_default bscdataclay/client:2.5.dev     \
	   NewAccount CityUser p4ssw0rd

echo "** Creating a new data contract in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
	   --network dataclay_default bscdataclay/client:2.5.dev     \
	   NewDataContract CityUser p4ssw0rd City CityUser

echo "** Register new model in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles \
	   -v $PWD/model/src:/classes --network dataclay_default     \
	   bscdataclay/client:2.5.dev NewModel CityUser p4ssw0rd     \
	   CityNS /classes python

mkdir -p stubs/ deploy

MODELDIR=deploy
rm -rf $MODELDIR/deploy
mkdir -p $MODELDIR/deploy
docker cp dataclay_dspython_1:/home/dataclayusr/dataclay/deploy/ $MODELDIR

echo " ===== Retrieving SQLITE LM into $MODELDIR/LM.sqlite  ====="
rm -f $MODELDIR/LM.sqlite
TABLES="account credential contract interface ifaceincontract opimplementations datacontract dataset accessedimpl accessedprop type java_type python_type memoryfeature cpufeature langfeature archfeature prefetchinginfo implementation python_implementation java_implementation annotation property java_property python_property operation java_operation python_operation metaclass java_metaclass python_metaclass namespace"
for table in $TABLES;
do
	docker exec -t dataclay_logicmodule_1 sqlite3 "//dataclay/storage/LM" ".dump $table" >> $MODELDIR/LM.sqlite
done

# Stop dockers
#./stop_dockers.sh

# PUSH DOCKERS TO DOCKERHUB 
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
DOCKER_BUILDER=$(docker buildx create)
PLATFORMS=linux/amd64,linux/arm64
#PLATFORMS=linux/arm64
docker buildx use $DOCKER_BUILDER
deploy docker buildx build -f Dockerfile.LM -t bscppc/dataclay-logicmodule:2.5.dev \
        --platform $PLATFORMS \
        --push .
deploy docker buildx build -f Dockerfile.DJ -t bscppc/dataclay-dsjava:2.5.dev \
        --platform $PLATFORMS \
        --push .
deploy docker buildx build -f Dockerfile.EE -t bscppc/dataclay-dspython:2.5.py36.dev \
        --platform $PLATFORMS \
        --push .
docker buildx rm $DOCKER_BUILDER

echo "** Removing existing dockers **"
docker-compose -f dataclay/docker-compose.yml kill
docker-compose -f dataclay/docker-compose.yml down -v

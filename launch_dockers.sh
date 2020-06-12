#!/bin/bash
export COMMAND_OPTS="--debug"

echo "** Removing existing dockers **"
docker-compose -f dataclay/docker-compose.yml down -v

echo "** Deploying dockers **"
docker-compose -f dataclay/docker-compose.yml up -d

echo "** Wait for dataClay to be alive **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles --network dataclay_default bscdataclay/client:2.4.dev WaitForDataClayToBeAlive 10 5

echo "** Registering new account in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles --network dataclay_default bscdataclay/client:2.4.dev NewAccount CityUser p4ssw0rd

echo "** Creating a new data contract in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles --network dataclay_default bscdataclay/client:2.4.dev NewDataContract CityUser p4ssw0rd City CityUser

echo "** Register new model in dataClay **"
docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles -v $PWD/model/src:/classes --network dataclay_default bscdataclay/client:2.4.dev NewModel CityUser p4ssw0rd CityNS /classes python
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

#echo "** Getting stubs from dataClay **"
#docker run --rm -v $PWD/cfgfiles:/home/dataclayusr/dataclay/cfgfiles -v $PWD/stubs:/stubs --network dataclay_default bscdataclay/client:2.4.dev GetStubs CityUser p4ssw0rd CityNS /stubs

#./stop_dockers.sh

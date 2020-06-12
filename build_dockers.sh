#!/bin/bash

# prepare architectures
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

DOCKER_BUILDER=$(docker buildx create) 
PLATFORMS=linux/amd64,linux/arm64
PLATFORMS=linux/amd64
#PLATFORMS=linux/arm64

docker buildx use $DOCKER_BUILDER

docker buildx build -f Dockerfile.LM -t bscppc/dataclay-logicmodule \
	--platform $PLATFORMS \
	--push .

echo " ===== Building docker dataclaydemo/dsjava  ====="
#docker buildx imagetools create --tag bscdataclay/dsjava:2.4.dev bscppc/dataclay-dsjava 
docker buildx build -f Dockerfile.DJ -t bscppc/dataclay-dsjava \
        --platform $PLATFORMS \
        --push .

echo " ===== Building docker dataclaydemo/dspython ====="
docker buildx build -f Dockerfile.EE -t bscppc/dataclay-dspython \
        --platform $PLATFORMS \
        --push .

docker buildx rm $DOCKER_BUILDER

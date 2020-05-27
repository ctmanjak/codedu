#!/bin/sh

if [ $1 ] && [ $DOCKER_PASSWORD ] && [ $DOCKER_USERNAME ]; then
    TAG=$1
    
    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

    docker build -t "ctmanjak/codedu_server:${TAG}" -f Dockerfile-falcon .

    docker push "ctmanjak/codedu_server:${TAG}"
else
    exit 1
fi
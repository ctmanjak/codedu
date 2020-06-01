#!/bin/bash


if [ $TRAVIS_BRANCH == "master" ]; then
    TAG="latest"
# elif [ $TRAVIS_BRANCH == "dev" ]; then
#     TAG="dev"
fi

if [ $TAG ] && [ $DOCKER_PASSWORD ] && [ $DOCKER_USERNAME ]; then
    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
    
    docker pull "ctmanjak/codedu_falcon:${TAG}"

    docker build -t "ctmanjak/codedu_falcon:${TAG}" -f docker/Dockerfile-falcon .

    docker push "ctmanjak/codedu_falcon:${TAG}"
fi
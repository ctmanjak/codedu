#!/bin/sh

if [ $TRAVIS_BRANCH == "dev" ]; then
    TAG="dev"
elif [ $TRAVIS_BRANCH == "master" ]; then
    TAG="latest"
fi

if [ $TAG ] && [ $DOCKER_PASSWORD ] && [ $DOCKER_USERNAME ]; then
    echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

    docker build -t "ctmanjak/codedu_server:${TAG}" -f Dockerfile-falcon .

    docker push "ctmanjak/codedu_server:${TAG}"
fi
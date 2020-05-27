#!/bin/sh

TARGET_IP=$1

docker build -t ctmanjak/codedu_server:falcon -f Dockerfile-falcon .

docker push ctmanjak/codedu_server:falcon

DOCKER_HOST=tcp://${TARGET_IP}:2375 docker stack deploy -c docker-compose.yml codedu
#!/bin/sh

TARGET_IP=$1

docker build -t ${TARGET_IP}:5000/codedu_server:falcon -f Dockerfile-falcon .

docker push ${TARGET_IP}:5000/codedu_server:falcon

DOCKER_HOST=tcp://${TARGET_IP}:2375 docker stack deploy -c docker-compose.yml codedu
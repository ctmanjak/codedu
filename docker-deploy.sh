#!/bin/sh

TARGET_DEPLOY_TCP=$1

docker build -t 15.165.181.246:5000/codedu_server:falcon -f Dockerfile-falcon .

docker push 15.165.181.246:5000/codedu_server:falcon

DOCKER_HOST=${TARGET_DEPLOY_TCP} docker stack deploy -c docker-compose.yml codedu
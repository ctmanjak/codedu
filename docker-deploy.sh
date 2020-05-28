#!/bin/sh

TARGET_IP=$(hostname -I | awk '{print $1}')
if [ $1 ]; then
    TARGET_IP=$1
fi

if nc -z -w5 $TARGET_IP 2375; then
    DOCKER_HOST=tcp://${TARGET_IP}:2375 docker stack deploy -c docker-compose.yml codedu
fi
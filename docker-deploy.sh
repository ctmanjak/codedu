#!/bin/sh

if [ $1 ]; then
    TARGET_IP=$1
    
    if nc -z -w5 $TARGET_IP 2375; then
        DOCKER_HOST=tcp://${TARGET_IP}:2375 docker stack deploy -c docker-compose.yml codedu
    fi
fi
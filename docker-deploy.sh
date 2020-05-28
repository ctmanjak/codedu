#!/bin/sh

TARGET_IP=$(hostname -I | awk '{print $1}')
if [ $1 ]; then
    TARGET_IP=$1
fi

if nc -z -w5 $TARGET_IP 2375; then
    MARIADB_CONF_VER=$(md5sum ./config/mariadb-default.cnf | awk '{print $1}')
    NGINX_CONF_VER=$(md5sum ./config/nginx-default.conf | awk '{print $1}')

    DOCKER_HOST=tcp://${TARGET_IP}:2375 \
    MARIADB_CONF_VER=$MARIADB_CONF_VER \
    NGINX_CONF_VER=$NGINX_CONF_VER \
    docker stack deploy -c docker-compose.yml codedu
fi
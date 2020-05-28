#!/bin/sh

TARGET_IP=$(hostname -I | awk '{print $1}')
if [ $1 ]; then
    TARGET_IP=$1
fi

if nc -z -w5 $TARGET_IP 2375; then
    export DOCKER_HOST=tcp://${TARGET_IP}:2375
    export MARIADB_CONF_VER=$(md5sum ./config/mariadb_default.cnf | awk '{print $1}')
    export NGINX_CONF_VER=$(md5sum ./config/nginx_default.conf | awk '{print $1}')

    if docker stack ls | grep -wq "codedu"; then
        if ! docker config ls | grep -wq "mariadb_conf-${MARIADB_CONF_VER}"; then
            PREV_MARIADB_CONF=$(docker service inspect codedu_mariadb | grep -oP '\"ConfigName\": "\K[^"]+' | uniq)

            docker config create "mariadb_conf-${MARIADB_CONF_VER}" ./config/mariadb_default.cnf
            docker service update --config-add "mariadb_conf-${MARIADB_CONF_VER}" --config-rm $PREV_MARIADB_CONF codedu_mariadb
        fi

        docker service update codedu_falcon

        if ! docker config ls | grep -wq "nginx_conf-${NGINX_CONF_VER}"; then
            PREV_NGINX_CONF=$(docker service inspect codedu_nginx | grep -oP '\"ConfigName\": "\K[^"]+' | uniq)

            docker config create "nginx_conf-${NGINX_CONF_VER}" ./config/nginx_default.conf
            docker service update --config-add "nginx_conf-${NGINX_CONF_VER}" --config-rm $PREV_NGINX_CONF codedu_nginx
        fi
    else
        docker stack deploy -c ./docker/docker-compose.yml codedu
    fi
fi
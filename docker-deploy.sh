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
        PREV_MARIADB_CONF=$(docker service inspect codedu_mariadb | grep -m1 -oP '\"ConfigName\": "\K[^"]+' | uniq)
        PREV_NGINX_CONF=$(docker service inspect codedu_nginx | grep -m1 -oP '\"ConfigName\": "\K[^"]+' | uniq)
        CURRENT_MARIADB_CONF="mariadb_conf-${MARIADB_CONF_VER}"
        CURRENT_NGINX_CONF="nginx_conf-${NGINX_CONF_VER}"

        if [ ! $PREV_MARIADB_CONF = $CURRENT_MARIADB_CONF ]; then
            if ! docker config ls | grep -wq $CURRENT_MARIADB_CONF; then
                docker config create $CURRENT_MARIADB_CONF ./config/mariadb_default.cnf
            fi
            docker service update \
                --config-add $CURRENT_MARIADB_CONF \
                --config-rm $PREV_MARIADB_CONF \
                codedu_mariadb
        fi

        docker service update codedu_falcon

        if [ ! $PREV_NGINX_CONF = $CURRENT_NGINX_CONF ]; then
            if ! docker config ls | grep -wq $CURRENT_NGINX_CONF; then
                docker config create $CURRENT_NGINX_CONF ./config/nginx_default.cnf
            fi
            docker service update \
                --config-add $CURRENT_NGINX_CONF \
                --config-rm $PREV_NGINX_CONF \
                codedu_nginx
        fi
    else
        docker stack deploy -c ./docker/docker-compose.yml codedu
    fi
fi
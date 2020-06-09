#!/bin/bash

TARGET_IP=$(hostname -I | awk '{print $1}')
if [ "${1}" ]; then
    TARGET_IP=$1
fi

if nc -zw3 "${TARGET_IP}" 2376; then
    export DOCKER_HOST="tcp://${TARGET_IP}:2376"
    export DOCKER_TLS_VERIFY=1

    if [ ! -d cert ]; then
        mkdir cert
    fi

    if [[ -f ca.pem && -f cert.pem && -f key.pem ]]; then
        cp {ca,cert,key}.pem cert/
    fi

    if [[ -f cert/ca.pem && -f cert/cert.pem && -f cert/key.pem ]]; then
        if [ ! -d ~/.docker ]; then
            mkdir ~/.docker
        fi
        cp cert/{ca,cert,key}.pem ~/.docker/
    else
        echo "cert files not found"
    fi
else
    echo "TARGET_IP is closed"
fi

if ! docker network ls | grep -wq codedu_net; then
    echo "creating codedu_net"
    docker network create --attachable --scope swarm codedu_net
fi
if ! docker ps | grep -wq nfs_server; then
    if docker ps -a | grep -wq nfs_server; then
        docker rm -f nfs_server
    fi
    
    echo "creating nfs_server"
    docker run -v nfs_image:/codedu/images -e NFS_EXPORT_0='/codedu/images *(rw,no_root_squash)' \
        --privileged --network codedu_net --network-alias nfs_server --name nfs_server \
        erichough/nfs-server
    
    # docker service create -d --mount type=volume,source=nfs_image,destination=/codedu/images \
    #     -e NFS_EXPORT_0='/codedu/images *(rw,no_root_squash)' --privileged -p 2049:2049 \
    #     --network codedu_net --name nfs_server erichough/nfs-server
fi

export NFS_SERVER_IP=$(docker inspect nfs_server | grep -oP '"IPAddress": "\K[\d.]+')

if [ "${NFS_SERVER_IP}" ]; then
    export MARIADB_CONF_VER=$(md5sum ./config/mariadb_default.cnf | awk '{print $1}')
    export NGINX_CONF_VER=$(md5sum ./config/nginx_default.conf | awk '{print $1}')

    DOCKER_COMPOSE_VER=$(md5sum ./docker/docker-compose.yml | awk '{print $1}')

    PREV_DOCKER_COMPOSE=$(docker config ls | grep -m1 -oP 'docker-compose-[^\s]+')
    if [ ! "${PREV_DOCKER_COMPOSE}" ]; then
        PREV_DOCKER_COMPOSE="not found"
    fi
    CURRENT_DOCKER_COMPOSE="docker-compose-${DOCKER_COMPOSE_VER}"

    if [ ! "${PREV_DOCKER_COMPOSE}" = "${CURRENT_DOCKER_COMPOSE}" ]; then
        echo "creating docker-compose config"
        docker config create $CURRENT_DOCKER_COMPOSE ./docker/docker-compose.yml
        echo "deploying codedu"
        docker stack deploy -c ./docker/docker-compose.yml codedu
        if [ ! "${PREV_DOCKER_COMPOSE}" = 'not found' ]; then
            docker config rm "${PREV_DOCKER_COMPOSE}"
        fi
    fi

    if docker stack ls | grep -wq "codedu"; then
        PREV_MARIADB_CONF=$(docker service inspect codedu_mariadb | grep -m1 -oP '\"ConfigName\": "\K[^"]+')
        PREV_NGINX_CONF=$(docker service inspect codedu_nginx | grep -m1 -oP '\"ConfigName\": "\K[^"]+')
        CURRENT_MARIADB_CONF="mariadb_conf-${MARIADB_CONF_VER}"
        CURRENT_NGINX_CONF="nginx_conf-${NGINX_CONF_VER}"

        if [[ ! "${PREV_MARIADB_CONF}" || ! "${PREV_MARIADB_CONF}" = "${CURRENT_MARIADB_CONF}" ]]; then
            if ! docker config ls | grep -wq "${CURRENT_MARIADB_CONF}"; then
                echo "creating mariadb config"
                docker config create "${CURRENT_MARIADB_CONF}" ./config/mariadb_default.cnf
            fi
            echo "updating codedu_mariadb"
            docker service update \
                --config-add source="${CURRENT_MARIADB_CONF}",target=/etc/mysql/mariadb.conf.d/default.cnf \
                --config-rm "${PREV_MARIADB_CONF}" \
                codedu_mariadb --force
        fi

        echo "updating codedu_falcon"
        docker pull ctmanjak/codedu_falcon
        docker service update codedu_falcon --force --image ctmanjak/codedu_falcon

        if [[ ! "${PREV_NGINX_CONF}" || ! "${PREV_NGINX_CONF}" = "${CURRENT_NGINX_CONF}" ]]; then
            if ! docker config ls | grep -wq "${CURRENT_NGINX_CONF}"; then
                echo "creating nginx config"
                docker config create "${CURRENT_NGINX_CONF}" ./config/nginx_default.conf
            fi
            echo "updating codedu_nginx"
            docker service update \
                --config-add source="${CURRENT_NGINX_CONF}",target=/etc/nginx/conf.d/default.conf \
                --config-rm "${PREV_NGINX_CONF}" \
                codedu_nginx --force
        fi
    else
        echo "codedu not found. deploying codedu"
        docker stack deploy -c ./docker/docker-compose.yml codedu
    fi
else
    echo "failed create nfs_server container. check docker logs nfs_server."
    echo "try modprobe nfs"
fi
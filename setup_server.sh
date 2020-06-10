#!/bin/bash

sh install_docker.sh

apt-get install nfs-common -y

if [ -d /etc/modules-load.d ]; then
    if [ -f /etc.modules-load.d/modules.conf ]; then
        echo "nfs" >> /etc/modules-load.d/modules.conf
    fi
fi

tmp_file="$HOME/docker-override.conf"

{
    echo "[Service]"; 
    echo "ExecStart=";
    echo "ExecStart=/usr/bin/dockerd"
} >$tmp_file

SYSTEMD_EDITOR="cp $tmp_file" systemctl edit docker

systemctl restart docker

rm $tmp_file

docker swarm init
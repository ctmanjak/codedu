#!/bin/sh

ip4=$(hostname -I | awk '{print $1}')

tmp_file="$HOME/docker-override.conf"

{
    echo "[Service]"; 
    echo "ExecStart=";
    echo "ExecStart=/usr/bin/dockerd -H tcp://${ip4}:2375 -H unix:///var/run/docker.sock";
} >$tmp_file

SYSTEMD_EDITOR="cp $tmp_file" systemctl edit docker

rm $tmp_file

docker swarm init
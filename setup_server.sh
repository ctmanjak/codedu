#!/bin/sh

ip4=$(hostname -I | awk '{print $1}')

CONTENT="[Service]\nExecStart=\nExecStart=/usr/bin/dockerd -H tcp://${ip4}:2375 -H unix:///var/run/docker.sock"

echo $CONTENT > /etc/systemd/system/docker.service.d/override.conf

service docker restart

docker swarm init
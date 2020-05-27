#!/bin/sh

ip4=$(hostname -I | awk '{print $1}')

CONTENT="[Service]\nExecStart=\nExecStart=/usr/bin/dockerd -H tcp://${ip4}:2375 -H unix:///var/run/docker.sock"

config_dir="/etc/systemd/system/docker.service.d"
config_file="${config_dir}/override.conf"

if [ ! -d "${config_dir}" ]; then
    mkdir "${config_dir}"
fi

if [ -f "${config_file}" ]; then
    if ! cat "${config_file}" | grep -q "${ip4}"; then
        service docker stop
        echo $CONTENT > "${config_file}"
        service docker start
    fi
fi

docker swarm init
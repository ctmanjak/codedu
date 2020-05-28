#!/bin/sh

if dpkg -s docker-ce | grep -q "Status: install ok installed" &&\
   dpkg -s docker-ce-cli | grep -q "Status: install ok installed" &&\
   dpkg -s containerd.io | grep -q "Status: install ok installed" &&\
   dpkg -s docker-compose | grep -q "Status: install ok installed";
then
    echo "docker is already installed"
    exit 1
else
    apt-get update

    DEBIAN_FRONTEND=noninteractive apt-get install -y\
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

    apt-key fingerprint 0EBFCD88

    add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"

    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose
fi
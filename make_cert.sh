#!/bin/bash

ip=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)
external_ip=$(curl https://ipinfo.io/ip)

if [ -d "/etc/docker" ]; then
    if [ ! -d "cert" ]; then
        mkdir cert
    fi

    cd cert

    openssl genrsa -aes256 -out ca-key.pem 4096
    openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem

    openssl genrsa -out server-key.pem 4096
    openssl req -subj "/CN=${HOSTNAME}" -sha256 -new -key server-key.pem -out server.csr

    echo subjectAltName = DNS:$HOSTNAME,IP:$ip,IP:127.0.0.1,IP:$external_ip >> extfile.cnf
    echo extendedKeyUsage = serverAuth >> extfile.cnf
    openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem \
        -CAcreateserial -out server-cert.pem -extfile extfile.cnf

    openssl genrsa -out key.pem 4096
    openssl req -subj '/CN=client' -new -key key.pem -out client.csr

    echo extendedKeyUsage = clientAuth > extfile-client.cnf
    openssl x509 -req -days 365 -sha256 -in client.csr -CA ca.pem -CAkey ca-key.pem \
    -CAcreateserial -out cert.pem -extfile extfile-client.cnf

    rm -v client.csr server.csr extfile.cnf extfile-client.cnf

    chmod -v 0400 ca-key.pem key.pem server-key.pem
    chmod -v 0444 ca.pem server-cert.pem cert.pem

    tar cvf ../secrets.tar ca.pem cert.pem key.pem
    echo "copy secrets.tar to dev-client and encrypting secrets.tar with travis for continuous deployment"
    echo "secrets.tar should be in {project_path}/docker/"
    echo "more info about encrypting file with travis in https://docs.travis-ci.com/user/encrypting-files/"

    if [ ! -f "/etc/docker/daemon.json" ]; then
        echo "{\"hosts\":[\"tcp://0.0.0.0:2376\"],\"tls\":true,\"tlsverify\":true,\"tlscacert\":\"$(pwd)/ca.pem\",\"tlscert\":\"$(pwd)/server-cert.pem\",\"tlskey\":\"$(pwd)/server-key.pem\"}" > /etc/docker/daemon.json
    else
        echo '/etc/docker/daemon.json already exists.'
    fi
else
    echo 'is docker installed?'
fi
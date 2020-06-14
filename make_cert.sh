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

    chmod -v 0444 {ca-key,key,server-key,ca,server-cert,cert}.pem

    if [ ! -d ~/.docker ]; then
        mkdir ~/.docker
    fi
    cp {ca,cert,key}.pem ~/.docker/

    tar cvf ../secrets.tar ca.pem cert.pem key.pem
    echo "copy secrets.tar to dev-client and encrypting secrets.tar with travis for continuous deployment"
    echo "secrets.tar should be in {project_path}/"
    echo "more info about encrypting file with travis in https://docs.travis-ci.com/user/encrypting-files/"
    echo -e "\nyou need run\n
    export DOCKER_HOST=tcp://${HOSTNAME}:2376 DOCKER_TLS_VERIFY=1\n
    or add it to ~/.bashrc for access docker"

    path_dj="/etc/docker/daemon.json"
    daemon_json="\"hosts\":[\"unix:///var/run/docker.sock\",\"tcp://0.0.0.0:2376\"],\"tls\":true,\"tlsverify\":true,\"tlscacert\":\"$(pwd)/ca.pem\",\"tlscert\":\"$(pwd)/server-cert.pem\",\"tlskey\":\"$(pwd)/server-key.pem\""
    if [ ! -f "${path_dj}" ]; then
        echo "{${daemon_json}}" > ${path_dj}
        systemctl restart docker
    else
        path_dj=
        echo '${path_dj} already exists.'
        echo -e "add\n
        ${daemon_json}\n
        to ${path_dj}\n
        ex) {\"some-key\":\"some-value\"} ->\n
            {\"some-key\":\"some-value\", ${daemon_json}}\n
        if ${path_dj} is empty, just put {${daemon_json}}"
        echo "lastly, restart docker service"
    fi
else
    echo 'is docker installed?'
fi
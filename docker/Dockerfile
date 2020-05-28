FROM ctmanjak/codedu_base:docker

WORKDIR /codedu
ADD ../config   /codedu/config
ADD ./docker-compose.yml /codedu/docker/docker-compose.yml

CMD ["docker", "stack", "deploy", "-c", "./docker/docker-compose.yml", "codedu"]
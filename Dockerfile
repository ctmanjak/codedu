FROM ctmanjak/codedu_base:docker

WORKDIR /codedu
ADD ./config   /codedu/config
ADD ./docker-compose.yml /codedu/config

CMD ["docker", "stack", "deploy", "-c", "docker-compose.yml", "codedu"]
FROM ubuntu:bionic

ADD ./config/sources.list /etc/apt/sources.list

RUN apt-get update &&\
    apt-get install -y libmariadb-dev wget gcc make zlib1g-dev libssl-dev

RUN wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz -O /tmp/Python-src.tgz &&\
    mkdir /tmp/Python-src &&\
    tar xzvf /tmp/Python-src.tgz -C /tmp/Python-src --strip-components 1 &&\
    /tmp/Python-src/configure && make /tmp/Python-src/ && make /tmp/Python-src/ install &&\
    rm -rf /tmp/*

WORKDIR /codedu
ADD ./config   /codedu/config
ADD ./look   /codedu/look
ADD ./test   /codedu/test
ADD ./docker-compose.yml   /codedu/docker-compose.yml 
ADD ./requirements.txt   /codedu/requirements.txt

RUN pip3 install -r requirements.txt

CMD ["sh", "run.sh"]
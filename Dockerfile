FROM ctmanjak/codedu_base:docker

WORKDIR /codedu
ADD ./   /codedu/

CMD ["sh", "run.sh"]
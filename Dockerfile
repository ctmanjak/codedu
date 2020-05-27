FROM 15.165.181.246:5000/codedu_base:docker

WORKDIR /codedu
ADD ./   /codedu/

CMD ["sh", "run.sh"]
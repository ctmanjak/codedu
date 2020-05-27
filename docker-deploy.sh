echo '{ "insecure-registries":["15.165.181.246:5000"] }' >> /etc/docker/daemon.json

docker build -t 15.165.181.246:5000/codedu_server:falcon -f Dockerfile-falcon .

# docker tag outsideris/demo:0.0.1 outsideris/demo:latest

docker push 15.165.181.246:5000/codedu_server:falcon
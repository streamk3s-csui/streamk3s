## Description

This container is a mechanism to post your messages and publish them to RabbitMQ broker

## Build image

docker build -f Dockerfile -t publish:v2.4 .
docker tag publish:v2.4 gkorod/publish:v2.4
docker push gkorod/publish:v2.4
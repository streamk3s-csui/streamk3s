## Description

This is a dummy operator that must be deployed as a container in the same pod with the publish operator in order to publish messages on a RabbitMQ broker. As our goal is only to test the communication between the two containers this dummy operator doesn't perform something fancy.
## Build image

docker build -f Dockerfile -t operator:v0.1
docker tag operator:v0.1 gkorod/operator:v0.1
docker push gkorod/operator:v0.1
## Description

This dummy operator, intended for deployment in Streaming Processing, is meant to be placed within the same container as the publish operator in a pod. Its sole purpose is to facilitate the exchange of messages on a RabbitMQ broker and does not involve any sophisticated operations since our primary objective is to test communication between the two containers.

## dummy_operator.py
This represents the main script within the example container, employing a function named <mark>receive_connection()</mark>. This function is crafted to establish a connection with the queue specified in the TOSCA model, enabling the retrieval of messages. The companion container's endpoint details are provided via environment variables: <mark>MY_POD_IP</mark>, <mark>API_PORT</mark>, and <mark>CONSUME_PATH</mark>.

To facilitate message reception, the operator container must feature an HTTP Post endpoint. To meet this requirement, the <a href=https://github.com/f-coda/Stream-Processing/blob/main/operator/dummy_operator.py>dummy_operator</a> operates <a href=https://github.com/f-coda/Stream-Processing/blob/main/operator/Interface.py>Interface.py</a> as a separate thread, employing the <mark>start_service()</mark> function.

## Interface.py

This script is designed to support two essential functions: sending and receiving messages. The sending process is executed through the <mark>send(message)</mark> function, which sends messages individually. For message reception, the example container employs a function called <mark>post()</mark>, establishing an HTTP Post endpoint named <mark>/post_message</mark>. This endpoint handles messages one at a time, storing them in a list.

## Build image

Each operator needs to be dockerized and hosted in a public repository. Otherwise, our Stream Processing Platform will not be able to access it.

``` shell
docker build -f Dockerfile -t operator:v0.1
docker tag operator:v0.1 gkorod/operator:v0.1
docker push gkorod/operator:v0.1
```
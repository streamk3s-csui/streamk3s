## Companion Container

The companion container facilitates message transmission and reception through two HTTP endpoints, leveraging the RabbitMQ broker:
* `/post_message`
* `/get_message`

For usage demonstrations, refer to the following examples:
* <a href="https://github.com/f-coda/Stream-Processing/blob/main/operator/Interface.py">Post request example</a>
* <a href="https://github.com/f-coda/Stream-Processing/blob/main/operator/dummy_operator.py">Get request example</a>

When a new pod is deployed on our platform, it incorporates both the function container provided by the developer and a specialized companion container. The accompanying figure illustrates the basic scenario featuring two operators—one for sending messages and the other for receiving them. Additionally, our platform supports operators capable of both sending and receiving messages.

![alt text](Stream%20Processing%20-%20companion.png)

## Build image

docker build -f Dockerfile -t publish:v2.4 .
docker tag publish:v2.4 gkorod/publish:v2.4
docker push gkorod/publish:v2.4
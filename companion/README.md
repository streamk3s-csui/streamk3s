## Description

The companion container facilitates message transmission and reception through two HTTP endpoints, leveraging the RabbitMQ broker:
* `/post_message`: This method invokes the <mark>publish_message(data,topic)</mark> function from the 
<a href=https://github.com/f-coda/Stream-Processing/blob/main/companion/publish.py>publish.py</a> script to send a message to the specified topic.
* `/get_message`: This method calls the <mark>consume_message(topic)</mark> function from the 
<a href=https://github.com/f-coda/Stream-Processing/blob/main/companion/consume.py>consumer.py</a> script to prefetch 10 messages from the designated topic. It then sends these messages back to the operator one by one.

The <mark>publish_message</mark> and <mark>consume_message</mark> functions reference the topic parameter, which is initialized by the environment variable named <mark>OUTPUT_TOPIC</mark> in the
<a href=https://github.com/f-coda/Stream-Processing/blob/main/companion/Interface.py>Interface.py</a> script. This naming convention is based on the concept that when an operator writes to a queue, it signifies an output, and when it reads from the queue, it represents an input. Similarly, there is also a topic named <mark>INPUT_TOPIC</mark> for the consumption scenario.

For usage demonstrations of the endpoints, refer to the <a href=https://github.com/f-coda/Stream-Processing/blob/main/operator/>operator</a> directory

## Deployment
When a new pod is deployed on our platform, it incorporates both the function container provided by the developer and a specialized companion container. The accompanying figure illustrates the basic scenario featuring two operators—one for sending messages and the other for receiving them. Additionally, our platform supports operators capable of both sending and receiving messages.

![alt text](Stream%20Processing%20-%20companion.png)

## Build image
``` shell
docker build -f Dockerfile -t publish:v2.4 .
docker tag publish:v2.4 gkorod/publish:v2.4
docker push gkorod/publish:v2.4
```
import os
import sys
import time
import logging
import json
import pika
import requests
from requests.auth import HTTPBasicAuth

#from MessageThread import CustomThread

message_list = []
logging.getLogger().setLevel(logging.INFO)
rabbit_ip = os.getenv("RABBIT_IP", "10.100.59.176")
user = 'user'
password = os.getenv("RABBITMQ_PASSWORD", "o1mB8moVLo")
application = os.getenv("APPLICATION", "#application")
credentials = pika.PlainCredentials(user, password)


def publish_message(data, topic):
    data_bytes = data.encode('utf-8')
    publish_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbit_ip,
                                  credentials=credentials,
                                  virtual_host=application))
    channel = publish_connection.channel()
    status = channel.queue_declare(queue=topic, durable=True)
    if status.method.message_count == 0:
        logging.info("queue empty")

    channel.basic_publish(exchange='',
                          routing_key=topic,
                          body=data_bytes,
                          properties=pika.BasicProperties(
                              delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                          ))

    print("message delivered", flush=True)
    publish_connection.close()
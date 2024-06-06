import os
import sys
import time
import logging
import json
import pika
import requests
from requests.auth import HTTPBasicAuth
import subprocess
from subprocess import PIPE

from systemd.journal import JournalHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# from MessageThread import CustomThread
consumer_list = []
message_list = []
log = logging.getLogger('Instancemanager consumer')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)


def callback(ch, method, properties, body):
    # thread = CustomThread()
    # thread.start()
    # thread.join()

    my_json = body.decode('utf8')
    data = json.loads(my_json)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    if data.get("namespace") and data.get("pod") and data.get("status"):
        if data.get("status") == "ended":
            namespace = data.get("namespace")
            pod = data.get("pod")
            x = subprocess.Popen(["kubectl delete -n " + namespace + " pod " + pod +" --now"], shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = x.communicate()
            if not "not found" in stderr.decode("utf-8"):
                message = "pod " + pod + " deleted"
            else:
                message = "looking for pods"
            print(message)
    else:
        message = "no operator pod has completed its processing."
    return message


def consume_message(termination_message):
    queue = termination_message.get("queue")
    user = os.getenv("RABBITMQ_USERNAME", "user")
    rabbit_ip = os.getenv("POD_IP", "ip")
    password = os.getenv("RABBITMQ_PASSWORD", "password")
    application = termination_message.get("namespace")
    credentials = pika.PlainCredentials(user, password)
    consume_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbit_ip,
                                  credentials=credentials,
                                  virtual_host=application,
                                  ))
    channel = consume_connection.channel()
    channel.basic_qos(prefetch_count=10)
    result = channel.basic_consume(queue=queue,
                                   auto_ack=False,
                                   on_message_callback=callback)
    print(' [*] Waiting for messages.')
    channel.start_consuming()
    return result

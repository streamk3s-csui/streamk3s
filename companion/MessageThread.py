import logging
import os
from threading import Thread

import requests
from requests.auth import HTTPBasicAuth


# custom thread
class CustomThread(Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.value = None

    # function executed in a new thread
    def run(self):
        # block for a moment
        rabbit_ip = os.getenv("RABBIT_IP", "#IP")
        rabbit_topic = os.getenv("INPUT_TOPIC", "#topic")
        password = os.getenv("RABBITMQ_PASSWORD", "o1mB8moVLo")
        application = os.getenv("APPLICATION", "#application")
        url = 'http://' + rabbit_ip + ':15672/api/queues/' + application + '/' + rabbit_topic
        logging.info(url)
        response = requests.get(url, auth=HTTPBasicAuth('user', password))
        logging.info(response.status_code)
        rabbit_json = response.json()
        logging.info(rabbit_json)
        messages = rabbit_json.get("messages")
        # store data in an instance variable
        self.value = messages
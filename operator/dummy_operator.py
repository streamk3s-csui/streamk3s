import json
import os
import subprocess
import threading
import time
import logging
import flask
from flask import Flask
import requests as requests

pod_ip = os.getenv("MY_POD_IP", "192.168.1.2")
api_port = os.getenv("API_PORT", "4321")
publish_path = os.getenv("PUBLISH_PATH", "/post_message")
consume_path = os.getenv("CONSUME_PATH", "/get_message")

logging.getLogger().setLevel(logging.INFO)


def start_service():
    subprocess.call(['python3', 'Interface.py'])


def receive_connection():
    ip = 'http://' + pod_ip + ':' + api_port + consume_path
    get_message = requests.get(ip)
    if get_message.status_code == 200:
        response = "successfully received message from API"
    else:
        response = "couldn't reach API, status error code: " + str(get_message.status_code)
    logging.info(response)


start = threading.Thread(target=start_service)
start.start()
time.sleep(15)
receive = threading.Thread(target=receive_connection)
receive.start()

import logging
import os
import json
import requests
import flask
from flask import Flask

app = Flask(__name__)
message_list = []
logging.getLogger().setLevel(logging.INFO)


pod_ip = os.getenv("MY_POD_IP", "192.168.1.2")
api_port = os.getenv("API_PORT", "4321")
publish_path = os.getenv("PUBLISH_PATH", "/post_message")
consume_path = os.getenv("CONSUME_PATH", "/get_message")


def send(message):
    ip = 'http://' + pod_ip + ':' + api_port + publish_path
    post = requests.post(ip, json=message)
    if post.status_code == 200:
        response = "successfully send message to API"
    else:
        response = "couldn't reach API, status error code: " + str(post.status_code)
    logging.info("message: " + str(message))
    logging.info(response)


@app.route("/post_message", methods=["POST"])
def post():
    json_data = flask.request.json
    message_list.append(json_data)
    send(json_data)
    logging.info('message in queue')
    logging.info(message_list)
    return 'message received'


app.run(host="0.0.0.0", port=4322, debug=True, use_reloader=False)

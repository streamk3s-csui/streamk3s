import logging
import os
import json
import threading
import consume
import flask
from flask import Flask
import publish

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)

logging.getLogger().setLevel(logging.INFO)


@app.route("/post_message", methods=["POST"])
def post():
    json_data = flask.request.json
    rabbit_topic = os.getenv("OUTPUT_TOPIC", "#topic")
    publish.publish_message(json_data, rabbit_topic)

    return json_data


@app.route("/get_message", methods=["GET"])
def get():
    rabbit_input_topic = os.getenv("INPUT_TOPIC", "topic-1")
    json_data = consume.consume_message(rabbit_input_topic)
    return json_data


app.run(host="0.0.0.0", port=4321)

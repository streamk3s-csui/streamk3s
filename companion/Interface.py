import logging
import os
import json
import consume
import flask
from flask import Flask, jsonify
import publish

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)

logging.getLogger().setLevel(logging.INFO)
termination = os.getenv("TERMINATION_QUEUE", "#termination")


@app.route("/post_message", methods=["POST"])
def post():
    json_string = flask.request.data.decode("utf-8")

    try:
        json_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return jsonify({"error": "Invalid JSON data"}), 400

    if json_data.get("status") and termination != "#termination":
        logging.info(json_string)
        publish.publish_message(json_string, termination)
    if json_data.get("status") is None:
        logging.info(json_string)
        rabbit_queue = os.getenv("OUTPUT_QUEUE", "#queue")
        publish.publish_message(json_string, rabbit_queue)

    return jsonify(json_data)


@app.route("/get_message", methods=["GET"])
def get():
    rabbit_input_queue = os.getenv("INPUT_QUEUE", "queue-1")
    json_data = consume.consume_message(rabbit_input_queue)
    return json_data


app.run(host="0.0.0.0", port=4321)

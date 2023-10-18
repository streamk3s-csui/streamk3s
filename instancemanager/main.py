from consume import consume_message
import os
import subprocess
import logging
import json


from flask import Flask, request
import multiprocessing

app = Flask(__name__)


def process_data(data):
    # Simulate some time-consuming task
    # Replace this with your actual data processing logic
    print('Processing data:', data)


@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()  # Get JSON data from the POST request
    logging.getLogger().setLevel(logging.INFO)
    rabbit_input_topic = data.get("topic")
    json_data = consume_message(rabbit_input_topic)
    namespace = json_data.get("namespace")
    pod = json_data.get("pod")
    command = "kubectl delete -n " + namespace + " pod " + pod
    logging.info(command)
    subprocess.call(["kubectl delete -n " + namespace + " pod " + pod], shell=True)
    logging.info("pod " + pod + " deleted")
    # Start a new process to process the data in parallel
    process = multiprocessing.Process(target=process_data, args=(data,))
    process.start()

    # Respond to the client immediately
    return 'Data received and processing started in a separate process.'


if __name__ == '__main__':
    app.run(debug=True)
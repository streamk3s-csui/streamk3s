from consume import consume_message
import os
import subprocess
import logging
from systemd.journal import JournalHandler
import json

from flask import Flask, request
import multiprocessing

app = Flask(__name__)
log = logging.getLogger('Instancemanager')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

def process_data(data):
    # Simulate some time-consuming task
    # Replace this with your actual data processing logic
    json_data = consume_message(data)
    namespace = json_data.get("namespace")
    pod = json_data.get("pod")
    command = "kubectl delete -n " + namespace + " pod " + pod
    log.info(command)
    subprocess.call(["kubectl delete -n " + namespace + " pod " + pod], shell=True)
    log.info("pod " + pod + " deleted")


@app.route('/init', methods=['POST'])
def receive_data():
    data = request.get_json()  # Get JSON data from the POST request
    log.info(data)
    rabbit_input_topic = data.get("topic")
    log.info(rabbit_input_topic)
    # Start a new process to process the data in parallel
    process = multiprocessing.Process(target=process_data, args=(rabbit_input_topic,))
    process.start()



    # Respond to the client immediately
    return 'Data received and processing started in a separate process.'


if __name__ == '__main__':
    app.run(debug=True, port=4004)

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


def init_process_logging():
    # Configure the logging handler for the current process
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def process_data(data):
    # Simulate some time-consuming task
    # Replace this with your actual data processing logic
    init_process_logging()
    queue = data.get("queue")
    logging.info(queue)
    namespace = data.get("namespace")
    logging.info(namespace)
    json_data = consume_message(queue, namespace)
    namespace = json_data.get("namespace")
    pod = json_data.get("pod")
    command = "kubectl delete -n " + namespace + " pod " + pod
    log.info(command)
    subprocess.call(["kubectl delete -n " + namespace + " pod " + pod], shell=True)
    log.info("pod " + pod + " deleted")


@app.route('/init', methods=['POST'])
def receive_data():
    data = request.get_json()  # Get JSON data from the POST request
    # Start a new process to process the data in parallel
    process = multiprocessing.Process(target=process_data, args=(data,))
    process.start()

    # Respond to the client immediately
    return 'Data received and processing started in a separate process.'


if __name__ == '__main__':
    app.run(debug=True, port=4004)

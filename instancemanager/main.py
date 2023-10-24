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


def process_data(termination_list):
    # Simulate some time-consuming task
    # Replace this with your actual data processing logic
    init_process_logging()
    consume_message(termination_list)


@app.route('/init', methods=['POST'])
def receive_data():
    termination_list = request.get_json()  # Get JSON data from the POST request
    # Start a new process to process the data in parallel
    process = multiprocessing.Process(target=process_data, args=(termination_list,))
    process.start()

    # Respond to the client immediately
    return 'Data received and processing started in a separate process.'


if __name__ == '__main__':
    app.run(debug=True, port=4004)

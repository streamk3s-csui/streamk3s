import requests

import consume
import os




def find_vhosts():
    # RabbitMQ credentials
    user = os.getenv("RABBITMQ_USERNAME", "name")
    rabbit_ip = os.getenv("POD_IP", "ip")
    password = os.getenv("RABBITMQ_PASSWORD", "password")

    rabbitmq_api_url = 'http://'+rabbit_ip+':15672/api/vhosts'  # Replace with your RabbitMQ Management API URL
    # Basic authentication header for RabbitMQ Management API
    auth_header = (user, password)

    # Make a GET request to retrieve vhosts
    response = requests.get(rabbitmq_api_url, auth=auth_header)

    vhosts = response.json()
    print("Available vhosts:")
    for vhost in vhosts:
        print(vhost['name'])
    return vhosts


import os
import requests


def find_queues():
    # RabbitMQ credentials
    user = os.getenv("RABBITMQ_USERNAME", "name")
    rabbit_ip = os.getenv("POD_IP", "ip")
    password = os.getenv("RABBITMQ_PASSWORD", "password")

    rabbitmq_api_url = f'http://'+rabbit_ip+':15672/api/queues'  # RabbitMQ Management API URL for queues
    # Basic authentication header for RabbitMQ Management API
    auth_header = (user, password)

    # Make a GET request to retrieve queues
    response = requests.get(rabbitmq_api_url, auth=auth_header)

    # Check if the request was successful
    if response.status_code == 200:
        queues = response.json()
        print("Available queues:")
        for queue in queues:
            print(queue['name'])
        return queues
    else:
        print(f"Failed to retrieve queues. Status code: {response.status_code}")
        return None




vhosts = find_vhosts()
queues = find_queues()
rabbit_input_topic = os.getenv("INPUT_TOPIC", "topic-2")
json_data = consume.consume_message(rabbit_input_topic)
print(json_data)


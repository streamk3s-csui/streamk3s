from consume import consume_message
import os
import subprocess
import logging
import json

logging.getLogger().setLevel(logging.INFO)
rabbit_input_topic = os.getenv("INPUT_TOPIC", "topic-2")
json_data = consume_message(rabbit_input_topic)
namespace = json_data.get("namespace")
pod = json.get("pod")
command = "kubectl delete -n "+namespace+" pod "+pod
print(command)
subprocess.call(["kubectl delete -n "+namespace+" pod "+pod], shell=True)
logging.info("pod "+ pod+ " deleted")

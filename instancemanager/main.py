import consume
import os


rabbit_input_topic = os.getenv("INPUT_TOPIC", "topic-2")
json_data = consume.consume_message(rabbit_input_topic)
print(json_data)


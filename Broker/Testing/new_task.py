#!/usr/bin/env python3
import sys

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

channel.queue_declare(queue="task_queue", durable=True)  #the server will keep the message, even if it crashes or quits

message = " ".join(sys.argv[1:]) or "Hello World!"
message_with_token = f"{message}|{session_token}"  # add the token to the message

channel.basic_publish(
    exchange="",
    routing_key="task_queue",
    body=message,
    body=message_with_token,  # the message will be with the token
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
    ),
)
print(f" [x] Sent {message_with_token}")
connection.close()

# These came from the tutorials

"""__sumary__
    LongSpotWorker is a worker file that will run to handle spotify related messages on the queue
"""
import pika
import mysql.connector
import json
import spotipy
import spotipy.util as util
import time
import datetime
import sys
import os
from dotenv import load_dotenv

import LongDB

load_dotenv()

# Load all env variables

SPOT_USER = os.getenv("SPOT_USER")
SPOT_PASS = os.getenv("SPOT_PASS")
SPOT_VHOST = os.getenv("SPOT_VHOST")
SPOT_QUEUE = os.getenv("SPOT_QUEUE")
SPOT_EXCHANGE = os.getenv("SPOT_EXCHANGE")
SPOT_PORT = os.getenv("SPOT_PORT")
SPOT_HOST = os.getenv("SPOT_HOST")


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )


# TODO: Fill out the request processor with necessary info
def request_processor(ch, method, properties, body):
    try:
        request = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        print("Error decoding incoming JSON")
        # TODO: save this as a log file as well
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"incoming request: {request}")
    if "type" not in request:
        print(f"{request}")
        # TODO: save this as a log file as well
        response = "ERROR: unsupported message type"
    else:
        request_type = request["type"]
        if request_type == "":
            # response = do_login(request["useremail"], request["password"])
        elif request_type == "":
            # print("Received session validation request")
            # response = do_validate(request["sessionId"])
        elif request_type == "":
            # print("Received registration request")
            # response = do_register(
            #     request["useremail"],
            #     request["password"],
            #     request["first_name"],
            #     request["last_name"],
            # )
        else:
            response = {
                "returnCode": "0",
                "message": "Server received request and processed it successfully",
            }



    print(f"We should have a response here if we're publishing...{response}")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    # Maybe auto ack? I'm not sure. TODO: verify?
    ch.basic_ack(delivery_tag=method.delivery_tag)

    pass


# TODO: sort out auto creation of queue and assignment to spotVHOST, update rmq to reflect autodelete once done

creds = pika.PlainCredentials(username=SPOT_USER, password=SPOT_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.68.65", port=5672, credentials=creds, virtual_host=SPOT_VHOST
    )
)
channel = connection.channel()
channel.queue_declare(queue=SPOT_QUEUE, durable=True)
channel.queue_bind(exchange=SPOT_EXCHANGE, queue=SPOT_QUEUE)
print(
    " [*] Waiting for a message from the webserver from spotify requests. To exit, press Ctrl+C"
)
channel.basic_consume(queue=SPOT_QUEUE, on_message_callback=request_processor)
print(" [x] Awaiting Spotify User requests")
channel.start_consuming()

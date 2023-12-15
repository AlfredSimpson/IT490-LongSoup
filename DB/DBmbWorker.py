import pika
import os, sys, json, random
from datetime import datetime, timedelta
import bcrypt
import pymongo
import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
BROKER_HOST = os.getenv("BROKER_HOST")
BROKER_USER = os.getenv("BROKER_USER")
BROKER_PASS = os.getenv("BROKER_PASS")
BROKER_VHOST = os.getenv("BROKER_VHOST")
BROKER_QUEUE = os.getenv("BROKER_QUEUE")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE")


# Message board info

MB_HOST = os.getenv("MBOARD_HOST")
MB_USER = os.getenv("MBOARD_USER")
MB_PASS = os.getenv("MBOARD_PASS")
MB_V = os.getenv("MBOARD_VHOST")
MB_Q = os.getenv("MBOARD_QUEUE")
MB_X = os.getenv("MBOARD_EXCHANGE")


def load_messages(uid, board, limit=20):
    """# load_messages
    This function takes in a user ID and a board name and returns the messages for that board.

    Args:
        uid (_type_): _description_
        board (_type_): _description_
        limit (_type_): _description_

    Returns:
        _type_: _description_
    """
    return {"returnCode": 0, "messages": []}


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


"""
def do_validate(usercookieid, session_id):
    # This takes in the sessionID and validates it by checking the database. If the sessionTable shows that the session is valid for the user, then it returns a boolean True. Otherwise, it returns a boolean False.
    validity = db.validate_session(usercookieid, session_id)
    # TODO: add this to the logging system
    # TODO: fix return statements, port validate_session
    print(f"\nvalidate_session returned: {validity}\n")
    return validity
"""


def request_processor(ch, method, properties, body):
    """# request_processor
    Takes in ch, method, properties, and body as arguments and processes the request based on the type of request received.

    Args:
        ch (_type_):
        method (_type_): _description_
        properties (_type_): _description_
        body (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Try / except added just in case bad JSON is received
    try:
        request = json.loads(body.decode("utf-8"))
        logging.debug(f"\nReceived request: {request}\n")
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "loadMessages":
                print(f'\n Received a request to load Messages: {request}\n')
                response = 
                pass
            case "postMessage":
                response = ""
                pass
            case _:
                # Default case - basically, all else failed.
                response = {
                    "returnCode": 0,
                    "message": "Server received request and processed - no action taken. Unknown type",
                }

    # Send the response back to the client
    print(f"\nWe should have a response here if we're publishing...{response}")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


creds = pika.PlainCredentials(username=MB_USER, password=MB_PASS)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=MB_HOST, port=5672, credentials=creds, virtual_host=MB_V, heartbeat=0
    )
)

channel = connection.channel()
channel.queue_declare(queue=MB_Q, durable=True)
channel.queue_bind(exchange=MB_X, queue=MB_Q)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=MB_Q, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()

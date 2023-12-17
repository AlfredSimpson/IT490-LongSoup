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

# Primary Mongo DB
MB_MAIN = os.getenv("MONGO_DB")
MB_MAIN_USER = os.getenv("MONGO_USER")
MB_MAIN_PASS = os.getenv("MONGO_PASS")

# Messageboard Mongo info
MB_DB_USER = os.getenv("MB_MONGO_USER")
MB_DB_PASS = os.getenv("MB_MONGO_PASS")
MB_DB = os.getenv("MB_MONGO_DB")

# Connect to the database - we're going to use cgs_mb

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/" % (MB_DB_USER, MB_DB_PASS)
)

db = myclient[MB_DB]


mboard_schema = {
    "post_id": "int",
    "uid": "int",
    "board": "string",
    "timestamp": "string",
    "message": "string",
}


def get_next_post_id():
    """# get_next_post_id
    This function gets the most recent post ID from the database and returns it plus one.
    """
    # Get the most recent post ID from the database
    # If there are no posts, return 1
    # Otherwise, return the most recent post ID + 1
    next_id = 0

    col = db.messages

    highest_id = col.find_one(sort=[("post_id", -1)])
    if highest_id:
        next_id = 1
        next_id += highest_id["post_id"]
    else:
        next_id = 1
    return next_id


def post_message(uid, board, message):
    """# post_message
    This function takes in a user ID, a board name, and a message and posts the message to the message board.

    Args:
        uid (_type_): _description_
        board (_type_): _description_
        message (_type_): _description_
        session_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    # We should now store this message in the database, along with the a human readable timestamp, the userid, and the board name.
    # Start with time:
    now = datetime.now()
    timestamp = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(f"\nTimestamp: {timestamp}\nNow: {now}\n")
    post_id = get_next_post_id()
    print(f"\nPost ID: {post_id}\n")

    # Now, we need to connect to the database and insert the message.
    #! If we want to use individual message boards for each genre - we'll call db[board] instead of db.messages
    #! TODO: We also need to take a username - or get it somehow.
    col = db.messages
    new_message = {
        "post_id": post_id,
        "uid": uid,
        "timestamp": timestamp,
        "message": message,
    }
    try:
        col.insert_one(new_message)
        print(f"\nMessage inserted: {new_message}\n")
    except Exception as e:
        print(f"\nError inserting message: {e}\n")
        return {"returnCode": 1, "message": "Error inserting message"}
    return {"returnCode": 0, "message": "Message posted"}


def get_messages(board, limit=20):
    # This is different than load_messages - it will be a helper function for post_message and for auto refreshing the message board.
    # This function will return the most recent messages for a given board.

    # First we connect to the messages table in the db
    col = db.messages
    #! If we want to use individual message boards for each genre - we'll call db[board] instead of db.messages

    try:
        messages = col.find().sort("timestamp", -1).limit(limit)

        # First, we'll create an empty list to hold the messages
        message_list = []
        # Now we'll loop through the messages and add them to the list
        for message in messages:
            message_list.append(
                {
                    "message": message["message"],
                    "timestamp": message["timestamp"],
                    "uid": message["uid"],
                }
            )
        return message_list
        # Now we'll return the list of messages
        # return {
        #     "returnCode": 0,
        #     "message": "Succcessfully retrieved messages",
        #     "message_list": message_list,
        # }
    except Exception as e:
        print(f"\nError retrieving messages: {e}\n")
        message_list = []
        return message_list
        # return {
        #     "returnCode": 1,
        #     "message": "Error retrieving messages",
        #     message_list: [],
        # }


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
    # data = [
    #     {"author": "Me", "date": "today", "message": "Hello, World!"},
    #     {"author": "You", "date": "yesterday", "message": "Hello, World!"},
    # ]

    # First, we'll get the messages. We'll ignore board for now - that comes later.
    data = get_messages(board, limit)
    print(f"\nData: {data}\n")

    return {"returnCode": 0, "message": "success", "messages": data}


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


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
                print(f"\n Received a request to load Messages: {request}\n")
                response = load_messages(
                    request["uid"], request["board"], request["limit"]
                )
                pass
            case "postMessage":
                print(f"\n Received a request to post a message: {request}\n")
                response = post_message(
                    request["uid"],
                    request["board"],
                    request["message"],
                )
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

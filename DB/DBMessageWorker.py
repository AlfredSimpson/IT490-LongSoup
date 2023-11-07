import pika
import os, sys, json, random
import datetime

# import LongMongoDB

# import LongDB deprecated for now - will be used later
import pymongo
import logging
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()

# MongoDB Secrets
maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")
maindbhost = os.getenv("MONGO_HOST")

# Rabbit MQ Message Board Workers
mboard_user = os.getenv("MBOARD_USER")
mboard_pass = os.getenv("MBOARD_PASS")
mboard_db = os.getenv("MBOARD_DB")
mboard_vhost = os.getenv("MBOARD_VHOST")
mboard_queue = os.getenv("MBOARD_QUEUE")
mboard_exchange = os.getenv("MBOARD_EXCHANGE")
mboard_host = os.getenv("MBOARD_HOST")


myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]


vHost = mboard_vhost
queue2 = mboard_queue
exchange2 = mboard_exchange
host = mboard_host
rmq_user = mboard_user
rmq_pass = mboard_pass

users = db.users
messages = db.messages


def loadMessages(
    board_id=None,
):
    try:
        board_content = messages.find_one({"board_id": board_id})
        return {"returnCode": 0, "message": board_content}
    except:
        board_content = None
        return {"returnCode": 1, "message": "Error loading messages"}


def postMessage(uid=None, board_id=None, message=None):
    try:
        messages.find_one_and_update(
            {board_id: board_id}, {"$push": {"thread_content": message}}
        )
        return {"returnCode": 0, "message": "Message posted successfully"}
    except:
        return {"returnCode": 1, "message": "Error posting message"}


def getLastMessageId(board_id, thread_id):
    try:
        pass
    except:
        pass
    pass


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
    print(f"\nincoming request: {request}\n")
    if "type" not in request:
        print(f"\n{request}\n")
        logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "loadMessages":
                response = loadMessages(
                    request["board_id"],
                )
            case "postMessage":
                response = postMessage(
                    request["uid"], request["board_id"], request["message"]
                )
            case _:
                # Default case - basically, all else failed.
                response = {
                    "returnCode": 0,
                    "message": "Server received request and processed - no action taken. Unknown type",
                }

    print(f"\nWe should have a response here if we're publishing...{response}")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


creds = pika.PlainCredentials(username=rmq_user, password=rmq_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.68.65", port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()

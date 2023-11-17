import pika
import time
import logging
import os, sys, json
import pymongo
from dotenv import load_dotenv

load_dotenv()

"""
This worker will handle moving QA to Prod. It will be called indirectly by qa_worker.py, which will send a message to the queue.
Once the message is received, this worker will run the necessary scripts to move the code from QA to Prod.
"""
vHost = os.getenv("DEV_RELAY_VHOST")
D_Q = os.getenv("DEV_QUEUE")
D_X = os.getenv("DEV_EXCHANGE")
D_HOST = os.getenv("DEV_RELAY_HOST")
D_USER = os.getenv("DEV_RELAY_USER")
D_PASS = os.getenv("DEV_RELAY_PASS")


def newPackage():
    pass


def routePackage(location):
    """
    While we process the newPackage, we should trigger this function to route the package to the correct location. This will be done by the routing key.

    """
    pass


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
    try:
        request = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        # return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "new_package":
                response = newPackage(
                    request[""],
                    request[""],
                    request[""],
                    request[""],
                )
            case _:
                # Default case - basically, all else failed.
                response = {
                    "returnCode": 0,
                    "message": "Could not process request - invalid type specified",
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


creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=D_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=D_Q, durable=True)
channel.queue_bind(exchange=D_X, queue=D_Q)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=D_Q, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()

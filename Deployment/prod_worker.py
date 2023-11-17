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
vHost = os.getenv("PROD_RELAY_VHOST")
P_Q = os.getenv("PROD_QUEUE")
P_X = os.getenv("PROD_EXCHANGE")
P_HOST = os.getenv("PROD_RELAY_HOST")
P_USER = os.getenv("PROD_RELAY_USER")
P_PASS = os.getenv("PROD_RELAY_PASS")


def request_processor(ch, method, props, body):
    """# request_processor
    This function is called when a message is received on the queue. It will take the message, and run the appropriate scripts to move the code from QA to Prod.
    """
    print("\n[x] Received request to move code from QA to Prod\n")
    pass


creds = pika.PlainCredentials(username=P_USER, password=P_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=P_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=P_Q, durable=True)
channel.queue_bind(exchange=P_X, queue=P_Q)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=P_Q, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()

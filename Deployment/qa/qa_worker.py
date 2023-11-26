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
vHost = os.getenv("QA_RELAY_VHOST")
QA_Q = os.getenv("QA_QUEUE")
QA_X = os.getenv("QA_EXCHANGE")
QA_HOST = os.getenv("QA_RELAY_HOST")
QA_USER = os.getenv("QA_RELAY_USER")
QA_PASS = os.getenv("QA_RELAY_PASS")


def request_processor(ch, method, props, body):
    """# request_processor
    This function is called when a message is received on the queue. It will take the message, and run the appropriate scripts to move the code from QA to Prod.
    """
    print("\n[x] Received request to move code from QA to Prod\n")
    pass


creds = pika.PlainCredentials(username=QA_USER, password=QA_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=QA_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=QA_Q, durable=True)
channel.queue_bind(exchange=QA_X, queue=QA_Q)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=QA_Q, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()

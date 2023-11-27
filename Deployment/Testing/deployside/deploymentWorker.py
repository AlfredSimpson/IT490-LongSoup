import os
import shutil
import pymongo
import pika
import paramiko
import pysftp
import json
import time
import sys
import re
import subprocess
import logging
import threading


from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

host_user = os.getenv("remote_host_user")
host_pass = os.getenv("remote_host_pass")

db_name = "test_gather"
current = "current_packages"
previous = "previous_packages"
backups = "backup_packages"

IN_SERVERS = ["front", "back", "dmz"]

# Load the environmental variables
# First, the AMQP variables
vHost = os.getenv("DEPLOYMENT_vHOST")
D_USER = os.getenv("DEPLOYMENT_USER")
D_PASS = os.getenv("DEPLOYMENT_PASSWORD")
D_HOST = os.getenv("DEPLOYMENT_HOST")
D_Q = os.getenv("DEPLOYMENT_QUEUE")
D_X = os.getenv("DEPLOYMENT_EXCHANGE")

# Then the MongoDB variables
mongo_user = os.getenv("MONGO_USER_D")
mongo_pass = os.getenv("MONGO_PASSWORD_D")
mongo_host = os.getenv("MONGO_HOST_D")
mongo_port = os.getenv("MONGO_PORT_D")
mongo_db = os.getenv("MONGO_DB_D")


LOCAL_PATH = "/home/longsoup/DEPLOY/"


def get_version():
    # This function will
    pass


def deploy(cluster, server, file_path, file_name):
    # This funciton begins the deployment steps. We will need to:
    # 1. Connect to the server -- SUCCESS
    # 2. If it is, scp the file from its server to this 192.168.68.61 server. --- SUCCESS
    # 3. Once we have the file, we need to update our database with the new file information #! TODO
    # 4. Then we can update the previous information with the current information #! TODO
    # 5. Finally, we will scp from this server to it's next destination.  #! TODO
    host_name = server + "_" + cluster
    print(f"hostname = {host_name}")
    with pysftp.Connection(
        host=host_name, username=host_user, password=host_pass
    ) as sftp:
        print(f"\nConnected to {host_name}\n")

        # get_version() #! TODO - we'll need to keep strict naming conventions.
        # This is a temporary workaround for testing:
        # ! TODO - we'll want to eventually ONLY pass the file_name and then add the versionining.
        LOCAL_NAME = LOCAL_PATH + file_name
        # Get the file:
        sftp.get(file_path, LOCAL_NAME, callback=None, preserve_mtime=True)
        print(f"\nFile {file_name} downloaded to {LOCAL_PATH}\n")
        return {
            "returnCode": 0,
            "message": f"File {file_name} downloaded to Deployment Server",
        }


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


def request_processor(ch, method, properties, body):
    try:
        request = json.loads(body.decode("utf-8"))
        # logging.debug(f"\nReceived request: {request}\n")
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        # logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        # logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "test":
                response = "test"
            case "deploy":
                response = deploy(
                    request["cluster"],
                    request["server"],
                    request["file_path"],
                    request["file_name"],
                )
            case _:
                response = "ERROR: Invalid type specified by message"
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

import pika
import os, sys, json, random
from dotenv import load_dotenv
import logging


load_dotenv()

# This file will sit on our cluster vms, and will handle requests to send data to the deployment server.

vHost = "deployment"
D_Q = "dep_q"
D_USER = "longsoup"
D_PASS = "puosgnol"
D_X = "dep_x"
D_HOST = "192.168.68.51"


def send_message(msg):
    vHost = "deployment"
    D_Q = "dep_q"
    D_USER = "longsoup"
    D_PASS = "puosgnol"
    D_X = "dep_x"
    D_HOST = "192.168.68.51"
    creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=D_HOST, port=5672, credentials=creds, virtual_host=vHost
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=D_Q, durable=True)
    channel.exchange_declare(exchange=D_X, exchange_type="direct")
    channel.basic_publish(exchange=D_X, routing_key=D_Q, body=msg)
    print(f"Sent message to {D_Q} queue.")
    connection.close()


def package_sender():
    file_location = input("Enter the location of the directory you want to send: ")
    message = {
        "type": "test",
        "file_location": file_location,
    }
    send_message(message)


def main():
    package_sender()


if __name__ == "__main__":
    main()

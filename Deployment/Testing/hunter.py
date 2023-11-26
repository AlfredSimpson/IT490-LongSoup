import pika
import os, sys, json

# hunter.py will be used to send a message to our deployment server. This will be used to test the connection between the two machines.

# First, we'll set up the plaintext variables of the queues, etc below:

vHost = "deployment"
D_Q = "dep_q"
D_USER = "longsoup"
D_PASS = "puosgnol"
D_X = "dep_x"
D_HOST = "192.168.68.51"

# Next, we'll set up the connection to the deployment server:

creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
# Let's put the connection in a try/except block to catch any errors and to print success messages.

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=D_HOST, virtual_host=vHost, credentials=creds)
)
channel = connection.channel()
channel.queue_declare(queue=D_Q, durable=True)
print("[*] Connection to the deployment server was successful.")
print("[*] Sending a test message to the deployment server.")
channel.basic_publish(
    exchange="",
    routing_key=D_Q,
    body=json.dumps({"type": "test"}),
)

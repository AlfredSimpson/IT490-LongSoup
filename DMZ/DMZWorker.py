import pika
import json
from dotenv import load_dotenv
import requests
import os
from procedural_data_script import job_and_send_result  # Import the function from the other script

load_dotenv()
#DMZ connection
DMZ_HOST = os.getenv("DMZ_HOST")
DMZ_VHOST = os.getenv("DMZ_VHOST")
DMZ_QUEUE = os.getenv("DMZ_QUEUE")
DMZ_EXCHANGE = os.getenv("DMZ_EXCHANGE")
DMZ_USER = os.getenv("DMZ_USER")
DMZ_PASS = os.getenv("DMZ_PASS")
DMZ_PORT = os.getenv("DMZ_PORT")

print(f"DMZ_HOST: {DMZ_HOST}")
print(f"DMZ_VHOST: {DMZ_VHOST}")
print(f"DMZ_QUEUE: {DMZ_QUEUE}")
print(f"DMZ_EXCHANGE: {DMZ_EXCHANGE}")
print(f"DMZ_USER: {DMZ_USER}")
print(f"DMZ_PASS: {DMZ_PASS}")
print(f"DMZ_PORT: {DMZ_PORT}")

# RabbitMQ configuration
#rabbitmq_host = 'your_rabbitmq_host'
#rabbitmq_port = int('your_rabbitmq_port')

creds = pika.PlainCredentials(username=DMZ_USER, password=DMZ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=DMZ_HOST, port=DMZ_PORT, credentials = creds, virtual_host = DMZ_VHOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=DMZ_QUEUE, durable=True)
# Binding to exchange
channel.queue_bind(exchange=DMZ_EXCHANGE, queue=DMZ_QUEUE)

def callback(ch, method, properties, body):
    # Trigger the 'job_and_send_result()' function when a message is received
    print("message received, triggering script...")
    job_and_send_result()

# Set up the consumer
channel.basic_consume(queue=DMZ_QUEUE, on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

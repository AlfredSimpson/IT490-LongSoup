import pika
import json
from dotenv import load_dotenv
import requests
from procedural_data_script import job_and_send_result  # Import the function from the other script

load_dotenv()

# RabbitMQ configuration
rabbitmq_host = 'your_rabbitmq_host'
rabbitmq_port = int('your_rabbitmq_port')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='data_queue')

def callback(ch, method, properties, body):
    # Trigger the 'job_and_send_result()' function when a message is received
    job_and_send_result()

# Set up the consumer
channel.basic_consume(queue='data_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()


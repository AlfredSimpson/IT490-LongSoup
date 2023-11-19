import json
import pymongo
from pymongo import MongoClient
import pika
from dotenv import load_dotenv
import time as tm
import os

load_dotenv()

# Connect to MongoDB
maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")
maindbhost = os.getenv("MONGO_HOST")

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]

# RabbitMQ configuration
rabbitmq_host = 'your_rabbitmq_host'
rabbitmq_port = int('your_rabbitmq_port')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='data_queue')

def callback(ch, method, properties, body):
    # Parse the JSON data
    json_data = json.loads(body)

    # Insert the JSON data into the 'audioArtists' collection
    try:
        db.audioArtists.insert_one(json_data)
        print(f"Data for artist ID {json_data['artist_id']} saved to MongoDB")
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")

# Set up the consumer
channel.basic_consume(queue='data_queue', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

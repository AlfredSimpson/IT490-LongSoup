import json
import pymongo
from pymongo import MongoClient
import pika
from dotenv import load_dotenv
import time as tm
import os

load_dotenv()

#DMZ connection
DMZ_HOST = os.getenv("DMZ_HOST")
DMZ_VHOST = os.getenv("DMZ_VHOST")
DMZ_QUEUE = os.getenv("DMZ_QUEUE")
DMZ_EXCHANGE = os.getenv("dmzExchange")
DMZ_USER = os.getenv("DMZ_USER")
DMZ_PASS = os.getenv("DMZ_PASS")
DMZ_PORT = os.getenv("DMZ_PORT")

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
creds = pika.PlainCredentials(username=DMZ_USER, password=DMZ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=DMZ_HOST, port=DMZ_PORT, credentials = creds, virtual_host = DMZ_VHOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue=DMZ_QUEUE)

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
channel.basic_consume(queue=DMZ_QUEUE, on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

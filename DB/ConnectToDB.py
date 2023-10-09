#!/usr/bin/env python3
import pika, sys, os, mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
Host = os.getenv("HOST")
VHOST = os.getenv("VHOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASS")
DB = os.getenv("DB")


# - This starts the rmq connection

# Set the rabbit credentials
creds = pika.PlainCredentials(username="test", password="test")
# Establish a connection to rabbitmq
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.1.25", port=5672, credentials=creds, virtual_host="dbHost"
    )
)

channel = connection.channel()
# Declare the queue, always. We must also state it's durable if it is. it defaults to false.
channel.queue_declare(queue="dbQueue", durable=True)
# Send a message to the queue if we want to. if not we'll delete.
channel.basic_publish(exchange="", routing_key="dbQueue", body="hey who goes there")
print("sent message")
# Close the connection
connection.close()

# This starts the mysql connection
mydb = mysql.connector.connect(
    host="localhost", user="example", password="exampl3!", database="tester"
)

# print(mydb)

mycursor = mydb.cursor()

# Now use the cursor to execute a query on the db
mycursor.execute("SELECT * FROM test")

DB_results = mycursor.fetchall()

for x in DB_results:
    print(x)

#  Now we can close the connection
mydb.close()
# Also, this does nothing really so it needs real code.

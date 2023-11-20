import pika
import time as tm
import schedule
import os

#DMZ connection
DMZ_HOST = os.getenv("DMZ_HOST")
DMZ_VHOST = os.getenv("DMZ_VHOST")
DMZ_QUEUE = os.getenv("DMZ_QUEUE")
DMZ_EXCHANGE = os.getenv("dmzExchange")
DMZ_USER = os.getenv("DMZ_USER")
DMZ_PASS = os.getenv("DMZ_PASS")
DMZ_PORT = os.getenv("DMZ_PORT")

# RabbitMQ configuration
creds = pika.PlainCredentials(username=DMZ_USER, password=DMZ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=DMZ_HOST, port=DMZ_PORT, credentials = creds, virtual_host = DMZ_VHOST))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='dmzQueue')

def send_trigger_message():
    # Send a message to the RabbitMQ queue to trigger the 'job_and_send_result()' function on the DMZ server
    channel.basic_publish(exchange='dmzExchange', routing_key='dmzQueue', body='Trigger Job')

# You can call send_trigger_message() whenever you want to trigger the job on the DMZ server
send_trigger_message()

# Schedule the job
schedule.every(30).seconds.do(send_trigger_message)

# Keep the script running
while True:
    schedule.run_pending()
    tm.sleep(1)


# Close the connection after sending the message
#connection.close()


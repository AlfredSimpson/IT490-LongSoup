import pika
import time as tm
import schedule

# RabbitMQ configuration
rabbitmq_host = 'your_rabbitmq_host'
rabbitmq_port = int('your_rabbitmq_port')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
channel = connection.channel()

# Declare the queue
channel.queue_declare(queue='data_queue')

def send_trigger_message():
    # Send a message to the RabbitMQ queue to trigger the 'job_and_send_result()' function on the DMZ server
    channel.basic_publish(exchange='', routing_key='data_queue', body='Trigger Job')

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


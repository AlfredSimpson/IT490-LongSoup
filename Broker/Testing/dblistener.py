import pika, mysql.connector

vHost = "tempHost"
queue2 = "tempQueue"
exchange2 = "tempExchange"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="192.168.68.65", virtual_host=vHost)
)

channel = connection.channel()

channel.queue_declare(queue=queue2, durable=True)

channel.queue_bind(exchange=exchange2, queue=queue2)

print(" [*] Waiting for a message from the webserver. To exit, press Ctrl+C")


def callback(ch, method, properties, body):
    received_message = body.decode()
    message, session_token = received_message.split("|")  # Extract session token, will feed to new_task

    # Connect to MySQL and store the session token
    mydb = mysql.connector.connect(
        host="your_host",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO session_tokens (token) VALUES (%s)" # STORING THE TOKEN
    val = (session_token,)
    mycursor.execute(sql, val)
    mydb.commit()

    print(f"[x] Received message: {message}, session token: {session_token}")
    ch.basic_ack(deliver_tag=method.delivery_tag) #removes message from queue , delivery done



channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue=queue2, on_message_callback=callback)
channel.basic_publish(exchange=exchange2, routing_key=queue2, body="It's me")
channel.start_consuming()
#removes message from queue , delivery done#removes message from queue , delivery done#removes message from queue , delivery done#removes message from queue , delivery done#removes message from queue , delivery done#removes message from queue , delivery done
import requests
import json
import schedule
import time as tm
from dotenv import load_dotenv
import pika
import os

load_dotenv()

#DMZ connection
#DMZ connection
#DMZ connection
DMZ_HOST = os.getenv("DMZ_HOST")
DMZ_VHOST = os.getenv("DMZ_VHOST")
DMZ_QUEUE = os.getenv("DMZ_QUEUE")
DMZ_EXCHANGE = os.getenv("dmzExchange")
DMZ_USER = os.getenv("DMZ_USER")
DMZ_PASS = os.getenv("DMZ_PASS")
DMZ_PORT = os.getenv("DMZ_PORT")

# Establish a connection to RabbitMQ
creds = pika.PlainCredentials(username=DMZ_USER, password=DMZ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=DMZ_HOST, port=DMZ_PORT, credentials = creds, virtual_host = DMZ_VHOST))
channel = connection.channel()

# Declare a queue named 'data_queue'
channel.queue_declare(queue=DMZ_QUEUE)

# Function to read the last saved artist ID from a file
def read_last_artist_id():
    try:
        with open('last_artist_id.txt', 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None

# Function to save the current artist ID to a file
def save_artist_id(artist_id):
    with open('last_artist_id.txt', 'w') as file:
        file.write(str(artist_id))

def query_artist(artist_id):
    url = f'https://theaudiodb.com/api/v1/json/2/artist.php?i={artist_id}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        artist_data = response.json()
        
        # Check if the artist exists in the response
        if 'artists' in artist_data and artist_data['artists']:
            artist_info = artist_data['artists'][0]
            return {"artist_id": artist_id, "artist_name": artist_info['strArtist'], "data": artist_info}
        else:
            return {"artist_id": artist_id, "error": "No artist found"}

    except requests.exceptions.RequestException as e:
        return {"artist_id": artist_id, "error": f"Error querying artist: {e}"}

def job_and_send_result():
    # job() function logic here
    # Read the last saved artist ID from the file
    last_artist_id = read_last_artist_id()

    # If it's the first run or the last saved ID is None, start from a specific artist ID
    if last_artist_id is None:
        specific_artist_id = 111233
    else:
        specific_artist_id = last_artist_id + 1

    # Query the artist
    artist_data = query_artist(specific_artist_id)
    #print(json.dumps(artist_data, indent=2)) Prints JSON data in readable format

    # Save the current artist ID to the file
    save_artist_id(specific_artist_id)

    # Send it over RabbitMQ
    channel.basic_publish(exchange=DMZ_EXCHANGE, routing_key=DMZ_QUEUE, body=json.dumps(artist_data))

# Schedule the job
# schedule.every(30).seconds.do(job_and_send_result)

# Keep the script running
# while True:
#     schedule.run_pending()
#     tm.sleep(1)

# Close the RabbitMQ connection when done
# connection.close()

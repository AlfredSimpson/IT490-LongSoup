import pika
import os, sys, json, random
import schedule
import time as tm
from datetime import time, timedelta, datetime
import requests
import json
import pymongo
import logging
from dotenv import load_dotenv

load_dotenv()

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

def job():
    # Specify the artist ID you want to query
    specific_artist_id = 111233

    artist_data = query_artist(specific_artist_id)
    print(json.dumps(artist_data, indent=2))

# Schedule the job
schedule.every(30).seconds.do(job)

# Keep the script running
while True:
    schedule.run_pending()
    tm.sleep(1)


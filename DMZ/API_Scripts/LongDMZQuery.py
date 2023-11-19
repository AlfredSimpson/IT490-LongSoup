import pika
import os, sys, json, random
import schedule
import time as tm
from datetime import time, timedelta, datetime
import bcrypt
import requests

# import LongMongoDB

# import LongDB deprecated for now - will be used later
import pymongo
import logging
from dotenv import load_dotenv


load_dotenv()

def getArtists(artist):
    
    api_url = f'https://www.theaudiodb.com/api/v1/json/523532/search.php?s={artist}'

    # fetch the JSON data from the API
    response = requests.get(api_url)

    if response.status_code == 200:
        data = json.loads(response.content)
        # Insert the JSON data into the collection
        #db.boardData.insert_one(data)
        print(data)
    else:
        print(f"Failed to get artist from the API. Status code: {response.status_code}")

# Calls function with parameter 'artist_name' (any artist u want)

# schedule function
#schedule.every().hour.at("10:30").do(getArtists)
#while True:
    #schedule.run_pending()
    #tm.sleep(1)
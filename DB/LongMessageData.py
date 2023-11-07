import pymongo
import requests
import json

maindb = 'cgs'#os.getenv("MONGO_DB")
maindbuser = 'longestsoup'#os.getenv("MONGO_USER")
maindbpass = 'shorteststraw'#os.getenv("MONGO_PASS")
maindbhost = 'localhost'#os.getenv("MONGO_HOST")

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]

# Fetch and store API data (AudioDB)
def fetch_and_store_artist_track(artist_name, artist_track):
    # Construct the API URL with the artist name
    api_url = f'https://theaudiodb.com/api/v1/json/523532/searchtrack.php?s={artist_name}&t={artist_track}'

    # fetch the JSON data from the API
    response = requests.get(api_url)

    if response.status_code == 200:
        data = json.loads(response.content)
        # Insert the JSON data into the collection
        db.boardData.insert_one(data)
        print(f"Track for '{artist_name}' inserted into 'boardData'.")
    else:
        print(f"Failed to get songs by '{artist_name}' from the API. Status code: {response.status_code}")

# User prompt for artist name
artist_name = input("Enter the artist's name: ")
artist_track = input("Enter the artist's track:")

# Calls function with parameter 'artist_name' (any artist u want)
fetch_and_store_artist_track(artist_name, artist_track)

# end connection
myclient.close()

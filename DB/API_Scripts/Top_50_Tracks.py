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
def fetch_and_store_artist_track():
    api_url = f'https://theaudiodb.com/api/v1/json/523532/mostloved.php?format=track'

    # fetch the JSON data from the API
    response = requests.get(api_url)

    if response.status_code == 200:
        data = json.loads(response.content)
        # Insert the JSON data into the collection
        db.boardData.insert_one(data)
        print(f"Top 50 most loved tracks inserted into 'boardData'.")
    else:
        print(f"Failed to get songs from the API. Status code: {response.status_code}")

# Calls function with parameter 'artist_name' (any artist u want)
fetch_and_store_artist_track()

# end connection
myclient.close()



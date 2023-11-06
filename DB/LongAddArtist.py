import pymongo
import base64
import requests
import json

# Replace these with your valid Spotify API credentials
client_id = '10c241e9a6b944928d20497ef814ef7d'
client_secret = 'b1cb224681ee4f8ea9d3f54ea1a3966a'

# MongoDB connection details (replace with your actual values)
maindb = 'cgs'
maindbuser = 'longestsoup'
maindbpass = 'shorteststraw'
maindbhost = 'localhost'

# Connect to MongoDB
myclient = pymongo.MongoClient(f"mongodb://{maindbuser}:{maindbpass}@{maindbhost}:27017/{maindb}")
db = myclient[maindb]

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}

def search_for_artist(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    api_json = json.loads(result.content)

    if 'artists' in api_json and 'items' in api_json['artists']:
        artists = api_json['artists']['items']
        if artists:
            artist = artists[0]
            # Extract artist data from the API response
            spotify_name = artist['name']
            spotify_popularity = artist['popularity']
            genre_types = artist['genres']
            spotify_link = artist['external_urls']['spotify']
            spotify_id = artist['id']
            spotify_images = artist.get('images', [])

            # Insert the artist document into the 'Artists' collection
            artist_data = {
                "name": spotify_name,
                "popularity": spotify_popularity,
                "spotifyId": spotify_id,
                "spotifyUrl": spotify_link,
                "spotifyPictures": spotify_images,
            }
            artist_id = db.Artists.insert_one(artist_data).inserted_id

            # Insert genre documents into the 'Genres' collection and associate them with the artist
            for genre in genre_types:
                genre_data = {
                    "name": genre
                }
                genre_id = db.Genres.insert_one(genre_data).inserted_id
                # Associate the artist with the genre
                db.Artists.update_one({"_id": artist_id}, {"$push": {"genres": genre_id}})

            print("Successfully added artist and associated genres to the database")
        else:
            print("No artist found for the given name.")
    else:
        print("Error in the Spotify API response.")

# Get the access token
token = get_token()

# Search for an artist (e.g., Nirvana)
search_for_artist(token, 'Nirvana')
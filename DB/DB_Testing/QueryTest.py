import spotipy
from spotipy.oauth2 import SpotifyOAuth
import mysql.connector


# Set your Spotify API credentials
client_id = '10c241e9a6b944928d20497ef814ef7d'
client_secret = 'b1cb224681ee4f8ea9d3f54ea1a3966a'

# Initialize Spotipy with OAuth2 authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret))

# Set up your MySQL database connection
db_config = {
    'host': 'localhost',
    'user': 'example',
    'password': 'examp13!',
    'database': 'tester'
}

# Connect to the MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Define the artist's name or Spotify URI
artist_name = '6olE6TJLqED3rqDCT0FyPh'

# Search for the artist
results = sp.search(q=f'artist:{artist_name}', type='artist')
artist = results['artists']['items'][0]

# Get the top tracks of the artist
top_tracks = sp.artist_top_tracks(artist['id'], country='US')  # You can specify the country code

# Insert the top tracks into the MySQL database
for track in top_tracks['tracks'][:10]:
    song_name = track['name']
    
    # Insert the song into the MySQL database
    insert_query = "INSERT INTO songs (artist_name, song_name) VALUES (%s, %s)"
    data = (artist_name, song_name)
    
    try:
        cursor.execute(insert_query, data)
        conn.commit()
        print(f"Inserted {song_name} by {artist_name} into the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Close the database connection
conn.close()

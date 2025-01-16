import json

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_id = '37i9dQZEVXbJiZcmkrIHGU'
results = sp.playlist(playlist_id)
print(json.dumps(results, indent=4))

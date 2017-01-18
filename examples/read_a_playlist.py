from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

uri = 'spotify:user:spotifycharts:playlist:37i9dQZEVXbJiZcmkrIHGU'
username = uri.split(':')[2]
playlist_id = uri.split(':')[4]

results = sp.user_playlist(username, playlist_id)
print json.dumps(results, indent=4)

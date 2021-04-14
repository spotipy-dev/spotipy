from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlist_id = 'spotify:user:spotifycharts:playlist:37i9dQZEVXbJiZcmkrIHGU'
results = sp.playlist(playlist_id)
print(json.dumps(results, indent=4))

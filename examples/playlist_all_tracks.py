# get all non-local tracks of a playlist
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint as pp

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

while result['next']:
	result = sp.next(result)
	tracks.extend(result['items'])
for item in tracks:
	if item["is_local"] == True:
		tracks.remove(item)
		
return tracks

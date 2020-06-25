# get all non-local tracks of a playlist
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint as pp

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# load the first 100 songs
tracks = []
result = sp.playlist_tracks()
tracks.extend(result['items'])

# if playlist is larger than 100 song, continue loading it until end
while result['next']:
	result = sp.next(result)
	tracks.extend(result['items'])

# remove all local songs
for item in tracks:
	if item["is_local"] == True:
		tracks.remove(item)
		
return tracks

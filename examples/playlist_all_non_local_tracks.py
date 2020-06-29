# get all non-local tracks of a playlist
from pprint import pprint as pp
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

# playlist id of global top 50
PlaylistExample = '37i9dQZEVXbMDoHDwVN2tF'

# create spotipy client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# load the first 100 songs
tracks = []
result = sp.playlist_tracks(PlaylistExample)
tracks.extend(result['items'])

# if playlist is larger than 100 songs, continue loading it until end
while result['next']:
	result = sp.next(result)
	tracks.extend(result['items'])

# remove all local songs
for item in tracks:
	if item['is_local']:
		tracks.remove(item)

# print result
pp(tracks)

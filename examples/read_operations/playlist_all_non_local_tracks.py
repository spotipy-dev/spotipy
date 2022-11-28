# get all non-local tracks of a playlist
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

# playlist id of global top 50
PlaylistExample = '37i9dQZEVXbMDoHDwVN2tF'

# create spotipy client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# load the first 100 songs
tracks = []
result = sp.playlist_items(PlaylistExample, additional_types=['track'])
tracks.extend(result['items'])

# if playlist is larger than 100 songs, continue loading it until end
while result['next']:
    result = sp.next(result)
    tracks.extend(result['items'])

# remove all local songs
i = 0  # just for counting how many tracks are local
for item in tracks:
    if item['is_local']:
        tracks.remove(item)
        i += 1


# print result
print("Playlist length: " + str(len(tracks)) + "\nExcluding: " + str(i))

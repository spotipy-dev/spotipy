# shows artist info for a URN or URL
# scope is not required for this function

import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
response = sp.artist_top_tracks(urn)

for track in response['tracks']:
    print(track['name'])

# Shows all artists featured on an album

# usage: featured_artists.py spotify:album:[album urn]

from spotipy.oauth2 import SpotifyClientCredentials
import sys
import spotipy
from pprint import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:album:5yTx83u3qerZF7GRJu7eFk'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
album = sp.album(urn)

featured_artists = set()

items = album['tracks']['items']

for item in items:
    for ele in item['artists']:
        if 'name' in ele:
            featured_artists.add(ele['name'])

pprint(featured_artists)

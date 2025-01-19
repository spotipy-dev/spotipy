# shows album info for a URN or URL

import sys
from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:album:5yTx83u3qerZF7GRJu7eFk'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
album = sp.album(urn)
pprint(album)

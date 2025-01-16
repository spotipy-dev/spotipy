# shows track info for a URN or URL

import sys
from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

track = sp.track(urn)
pprint(track)

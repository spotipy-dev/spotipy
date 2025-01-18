# Shows artist info for a URN or URL

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = 'plamere'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace = True
user = sp.user(username)
pprint.pprint(user)

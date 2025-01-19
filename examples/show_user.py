# Shows artist info for a URN or URL

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

username = sys.argv[1] if len(sys.argv) > 1 else 'plamere'
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)
sp.trace = True
user = sp.user(username)
pprint.pprint(user)

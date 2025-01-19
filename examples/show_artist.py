# shows artist info for a URN or URL

import sys
from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

artist = sp.artist(urn)
pprint(artist)

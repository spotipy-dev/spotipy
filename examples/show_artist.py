# shows artist info for a URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

artist = sp.artist(urn)
pprint(artist)

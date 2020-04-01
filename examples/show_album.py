
# shows album info for a URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:album:5yTx83u3qerZF7GRJu7eFk'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
album = sp.album(urn)
pprint(album)

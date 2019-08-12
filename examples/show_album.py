
# shows album info for a URN or URL

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:album:5yTx83u3qerZF7GRJu7eFk'


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
album = sp.album(urn)
pprint.pprint(album)

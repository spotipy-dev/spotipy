# shows track info for a URN or URL

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
track = sp.track(urn)
pprint.pprint(track)

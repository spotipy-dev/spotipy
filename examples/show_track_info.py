# shows track info for a URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

track = sp.track(urn)
pprint(track)


# shows audiobook info for an ID, URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
from pprint import pprint

if len(sys.argv) > 1:
  urn = sys.argv[1]
else:
  urn = 'spotify:audiobook:7iHfbu1YPACw6oZPAFJtqe'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

audiobook = sp.audiobook(urn)
pprint(audiobook)

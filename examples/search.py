# shows artist info for a URN or URL

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

search_str = sys.argv[1] if len(sys.argv) > 1 else 'Radiohead'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
result = sp.search(search_str)
pprint.pprint(result)

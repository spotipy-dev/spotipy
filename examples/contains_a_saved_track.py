# Prints whether a track exists in your collection of saved tracks

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'

if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    print(f"Usage: {sys.argv[0]} track-id ...")
    sys.exit()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_saved_tracks_contains(tracks=[tid])
pprint.pprint(results)

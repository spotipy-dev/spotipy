# code example that demonstrates current_user_saved_tracks_contains(tracks=None) functionality
# Link to documentation -> https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.current_user_saved_tracks_contains
# Prints whether a track exists in your collection of saved tracks

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'

if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    print("Usage: %s track-id ..." % (sys.argv[0],))
    sys.exit()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_saved_tracks_contains(tracks=[tid])
pprint.pprint(results)

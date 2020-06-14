import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'

if len(sys.argv) > 1:
    tids = sys.argv[1]
else:
    print("Usage: %s track-id ..." % (sys.argv[0],))
    sys.exit()

    results = spotipy.current_user_saved_tracks_contains(tracks=tids)
    pprint.pprint(results)


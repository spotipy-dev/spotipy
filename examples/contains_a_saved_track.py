import pprint
import sys

import spotipy
import spotipy.util as util

scope = 'user-library-read'

if len(sys.argv) > 2:
    username = sys.argv[1]
    tids = sys.argv[2:]
else:
    print("Usage: %s username track-id ..." % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.current_user_saved_tracks_contains(tracks=tids)
    pprint.pprint(results)
else:
    print("Can't get token for", username)

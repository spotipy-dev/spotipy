
# Adds tracks to a playlist

import pprint
import sys

import spotipy
import spotipy.oauth2 as oauth2
import util

scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print "Usage: %s username" % (sys.argv[0],)
    sys.exit()

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.current_user_saved_tracks()
    pprint.pprint(results)
else:
    print "Can't get token for", username

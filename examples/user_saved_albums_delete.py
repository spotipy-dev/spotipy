"""
    Deletes user saved album

"""

import pprint
import sys
import json
import spotipy
import spotipy.util as util

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

scope = 'user-library-modify'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    uris = input("input a list of album URIs, URLs or IDs: ")
    uris = list(map(str, uris.split()))
    deleted = sp.current_user_saved_albums_delete(uris)
    print("Deletion successful.")

else:
    print("Can't get token for", username)

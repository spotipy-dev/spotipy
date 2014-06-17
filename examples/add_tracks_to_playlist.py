
# Adds tracks to a playlist

import pprint
import sys

import spotipy
import spotipy.oauth2 as oauth2
import util

if len(sys.argv) > 3:
    username = sys.argv[1]
    playlist_id = sys.argv[2]
    track_ids = sys.argv[3:]
else:
    print "Usage: %s username playlist_id track_id ..." % (sys.argv[0],)
    sys.exit()

scope = 'playlist-modify'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
    pprint.pprint(results)
else:
    print "Can't get token for", username

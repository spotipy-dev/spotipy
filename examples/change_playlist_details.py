
# Modify the details of a playlist (name, public, collaborative)

import sys

import spotipy
import spotipy.util as util

if len(sys.argv) > 3:
    username = sys.argv[1]
    playlist_id = sys.argv[2]
    name = sys.argv[3]

    public = None
    if len(sys.argv) > 4:
        public = sys.argv[4].lower() == 'true'

    collaborative = None
    if len(sys.argv) > 5:
        collaborative = sys.argv[5].lower() == 'true'

    description = None
    if len(sys.argv) > 6:
        description = sys.argv[6]

else:
    print ("Usage: %s username playlist_id name [public collaborative "
           "description]" % (sys.argv[0]))
    sys.exit()

scope = 'playlist-modify-public playlist-modify-private'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.user_playlist_change_details(
        username, playlist_id, name=name, public=public,
        collaborative=collaborative, description=description)
    print results
else:
    print "Can't get token for", username

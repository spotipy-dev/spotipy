# Shows the top artists for a user

import pprint
import sys

import spotipy
import spotipy.util as util
import simplejson as json

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    ranges = ['short_term', 'medium_term', 'long_term']
    for range in ranges:
        print "range:", range
        results = sp.current_user_top_artists(time_range=range, limit=50)
        for i, item in enumerate(results['items']):
            print i, item['name']
        print
else:
    print("Can't get token for", username)

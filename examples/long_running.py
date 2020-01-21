# long running example (need to be authenticated via oauth)

import sys
import time
from datetime import datetime

import spotipy
import spotipy.util as util

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Whoops, need your username!")
    print("usage: python user_playlists.py [username]")
    sys.exit()

SCOPE = ','.join([
    'user-modify-playback-state',
    'user-read-playback-state',
    'user-read-currently-playing'
])

oauth = util.prompt_for_user_token(
    username,
    redirect_uri="http://localhost/",
    scope=SCOPE)

if oauth:
    sp = spotipy.Spotify(auth=oauth)
    # sp.trace = True
    # sp.trace_out = True
    start = datetime.now()
    while True:
        current_playback = sp.current_playback()
        print(datetime.now() - start,
              "is_playing?",
              None if current_playback is None
              else current_playback['is_playing'])

        time.sleep(60)
else:
    print("Can't get token for", username)

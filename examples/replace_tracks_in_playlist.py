# Replaces all tracks in a playlist

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) > 3:
    playlist_id = sys.argv[1]
    track_ids = sys.argv[2:]
else:
    print("Usage: %s username playlist_id track_id ..." % (sys.argv[0],))
    sys.exit()

scope = 'playlist-modify-public'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user_id = sp.me()['id']

results = sp.user_playlist_replace_tracks(user_id, playlist_id, track_ids)
pprint.pprint(results)


# Replaces all tracks in a playlist

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) > 3:
    playlist_id = sys.argv[1]
    track_ids = sys.argv[2:]
else:
    print(f"Usage: {sys.argv[0]} playlist_id track_id ...")
    sys.exit()

scope = 'playlist-modify-public'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.playlist_replace_items(playlist_id, track_ids)
pprint.pprint(results)

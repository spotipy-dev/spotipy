# Removes tracks from a playlist

import pprint
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) > 2:
    playlist_id = sys.argv[1]
    track_ids_and_positions = sys.argv[2:]
    track_ids = []
    for t_pos in sys.argv[2:]:
        tid, pos = t_pos.split(',')
        track_ids.append({"uri": tid, "positions": [int(pos)]})
else:
    print(
        "Usage: %s playlist_id track_id,pos track_id,pos ..." %
        (sys.argv[0],))
    sys.exit()

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.playlist_remove_specific_occurrences_of_items(
    playlist_id, track_ids)
pprint.pprint(results)

# Shows a user's playlists (need to be authenticated via oauth)

import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Whoops, need a username!")
    print("usage: python user_playlists.py [username]")
    sys.exit()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

playlists = sp.user_playlists(username)

for playlist in playlists['items']:
    print(playlist['name'])
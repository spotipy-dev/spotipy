# Shows a user's playlists (need to be authenticated via oauth)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-read-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
playlists = sp.current_user_playlists()

for playlist in playlists['items']:
    print(playlist['name'])

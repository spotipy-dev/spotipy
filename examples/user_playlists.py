# Shows a user's playlists (need to be authenticated via oauth)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
playlists = sp.current_user_playlists()

for playlist in playlists['items']:
    print(playlist['name'])

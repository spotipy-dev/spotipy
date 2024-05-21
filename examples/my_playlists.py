# code example that demonstrates current_user_playlists(limit=50, offset=0) functionality
# Link to documentation -> https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.current_user_playlists
# Shows a user's playlists

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-read-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_playlists(limit=50)
for i, item in enumerate(results['items']):
    print("%d %s" % (i, item['name']))

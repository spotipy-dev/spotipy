# Add a list of items (URI) to a playlist (URI)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope="playlist-modify-private"
                                               ))

sp.playlist_add_items('playlist_id', ['list_of_items'])

# Deletes user saved album

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-modify'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

uris = input("input a list of album URIs, URLs or IDs: ")
uris = list(map(str, uris.split()))
deleted = sp.current_user_saved_albums_delete(uris)
print("Deletion successful.")

# Gets all the public playlists for the given
# user. Uses Client Credentials flow
#

import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

user = sys.argv[1] if len(sys.argv) > 1 else 'spotify'
playlists = sp.user_playlists(user)

while playlists:
    for i, playlist in enumerate(playlists['items']):
        print(f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}")
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

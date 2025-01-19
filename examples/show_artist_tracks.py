# shows tracks for the given artist

# usage: python tracks.py [artist name]

import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

if len(sys.argv) > 1:
    artist_name = ' '.join(sys.argv[1:])
    results = sp.search(q=artist_name, limit=20)
    for i, t in enumerate(results['tracks']['items']):
        print(' ', i, t['name'])

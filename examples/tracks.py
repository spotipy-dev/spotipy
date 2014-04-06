# shows tracks for the given artist

from __future__ import print_function
import spotipy
import sys
sp = spotipy.Spotify()

if len(sys.argv) > 1:
    artist_name = ' '.join(sys.argv[1:])
    tracks = sp.search(q=artist_name, limit=20)
    for i, t in enumerate(tracks['tracks']):
        print(' ', i, t['name'])

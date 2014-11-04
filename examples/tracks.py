# shows tracks for the given artist


import spotipy
import sys
sp = spotipy.Spotify()

if len(sys.argv) > 1:
    artist_name = ' '.join(sys.argv[1:])
    results = sp.search(q=artist_name, limit=20)
    for i, t in enumerate(results['tracks']['items']):
        print(' ', i, t['name'])

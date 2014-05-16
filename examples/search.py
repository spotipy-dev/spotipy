# shows artist info for a URN or URL

import spotipy
import sys
import pprint

if len(sys.argv) > 1:
    str = sys.argv[1]
else:
    str = 'Radiohead'

sp = spotipy.Spotify()
result = sp.search(str)
pprint.pprint(result)

# shows artist info for a URN or URL

import spotipy
import sys
import pprint

if len(sys.argv) > 1:
    search_str = sys.argv[1]
else:
    search_str = 'Radiohead'

sp = spotipy.Spotify()
result = sp.search(search_str)
pprint.pprint(result)

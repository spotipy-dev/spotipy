
# shows album info for a URN or URL

import spotipy
import sys
import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:album:5yTx83u3qerZF7GRJu7eFk'


sp = spotipy.Spotify()
album = sp.album(urn)
pprint.pprint(album)

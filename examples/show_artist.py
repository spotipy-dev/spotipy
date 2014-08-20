# shows artist info for a URN or URL

import spotipy
import sys
import pprint

if len(sys.argv) > 1:
    urn = sys.argv[1]
else:
    urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'

sp = spotipy.Spotify()

artist = sp.artist(urn)

pprint.pprint(artist)

# shows artist info for a URN or URL

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
import pprint

if len(sys.argv) > 1:
    search_str = sys.argv[1]
else:
    search_str = 'Radiohead'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
result = sp.search(search_str)
pprint.pprint(result)

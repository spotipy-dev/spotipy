from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint(result)

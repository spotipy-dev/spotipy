from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint(result)

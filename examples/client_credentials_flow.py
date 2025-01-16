from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint(result)

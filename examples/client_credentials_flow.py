from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint(result)

# What is this inteded to be an example of? Client credentials are retrieved in every other example, so I'm not sure this script is adding anything new. 
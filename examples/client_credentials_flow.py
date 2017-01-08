from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pprint

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_str = 'Muse'
result = sp.search(search_str)
pprint.pprint(result)

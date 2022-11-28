
# shows related artists for the given seed artist

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys

if len(sys.argv) > 1:
    artist_name = sys.argv[1]
else:
    artist_name = 'weezer'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
result = sp.search(q='artist:' + artist_name, type='artist')
try:
    name = result['artists']['items'][0]['name']
    uri = result['artists']['items'][0]['uri']

    related = sp.artist_related_artists(uri)
    print('Related artists for', name)
    for artist in related['artists']:
        print('  ', artist['name'])
except BaseException:
    print("usage show_related.py [artist-name]")

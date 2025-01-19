# shows related artists for the given seed artist

import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

artist_name = sys.argv[1] if len(sys.argv) > 1 else 'weezer'
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)
result = sp.search(q=f'artist:{artist_name}', type='artist')

try:
    name = result['artists']['items'][0]['name']
    uri = result['artists']['items'][0]['uri']

    related = sp.artist_related_artists(uri)
    print('Related artists for', name)
    for artist in related['artists']:
        print('  ', artist['name'])
except BaseException:
    print("usage show_related.py [artist-name]")

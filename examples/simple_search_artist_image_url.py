# Shows the name of the artist/band and their image by giving a link
import sys

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

name = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'Radiohead'
results = sp.search(q=f'artist:{name}', type='artist')
items = results['artists']['items']
if len(items) > 0:
    artist = items[0]
    print(artist['name'], artist['images'][0]['url'])

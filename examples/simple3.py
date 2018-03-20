import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='YOUR CLIENT ID HERE',
                                                      client_secret='YOUR CLIENT SECRET HERE')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


if len(sys.argv) > 1:
    name = ' '.join(sys.argv[1:])
else:
    name = 'Radiohead'

results = spotify.search(q='artist:' + name, type='artist')
items = results['artists']['items']
if len(items) > 0:
    artist = items[0]
    print(artist['name'], artist['images'][0]['url'])


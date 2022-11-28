# Gets all the public playlists for the given
# user. Uses Client Credentials flow
#

import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

user = 'spotify'

if len(sys.argv) > 1:
    user = sys.argv[1]

playlists = sp.user_playlists(user)

while playlists:
    for i, playlist in enumerate(playlists['items']):
        print(
            "%4d %s %s" %
            (i +
             1 +
             playlists['offset'],
             playlist['uri'],
             playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

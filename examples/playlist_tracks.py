from pprint import pprint

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

pl_id = 'spotify:playlist:5RIbzhG2QqdkaP24iXLnZX'
offset = 0

while True:
    response = sp.playlist_items(pl_id,
                                 offset=offset,
                                 fields='items.track.id,total',
                                 additional_types=['track'])

    if len(response['items']) == 0:
        break

    pprint(response['items'])
    offset = offset + len(response['items'])
    print(offset, "/", response['total'])

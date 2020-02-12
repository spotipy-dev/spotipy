from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

pl_id = 'spotify:playlist:5RIbzhG2QqdkaP24iXLnZX'
offset = 0

while True:
    response = sp.playlist_tracks(pl_id,
                                  offset=offset,
                                  fields='items.track.id,total')
    pprint(response['items'])
    offset = offset + len(response['items'])
    print(offset, "/", response['total'])

    if len(response['items']) == 0:
        break

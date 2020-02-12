from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from pprint import pprint

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

pl_id = 'spotify:playlist:5RIbzhG2QqdkaP24iXLnZX'
response = sp.playlist_tracks(pl_id, fields='items.track.id,total')
offset = 0

while len(response['items']) > 0:
    print(offset, "/", response['total'])
    response = sp.playlist_tracks(pl_id,
                                  offset=offset,
                                  fields='items.track.id,total')
    offset = offset + len(response['items'])
    pprint(response['items'])

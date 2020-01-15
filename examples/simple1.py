from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = sp.artist_albums(birdy_uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print((album['name']))

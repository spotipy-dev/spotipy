import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='YOUR CLIENT ID HERE',
                                                      client_secret='YOUR CLIENT SECRET HERE')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'


results = spotify.artist_top_tracks(lz_uri)

for track in results['tracks'][:10]:
    print('track    : ' + track['name'])
    print('audio    : ' + track['preview_url'])
    print('cover art: ' + track['album']['images'][0]['url'])
    print()
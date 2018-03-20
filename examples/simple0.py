import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='YOUR CLIENT ID HERE',
                                                      client_secret='YOUR CLIENT SECRET HERE')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

results = spotify.search(q='weezer', limit=20)
for i, t in enumerate(results['tracks']['items']):
    print(' ', i, t['name'])
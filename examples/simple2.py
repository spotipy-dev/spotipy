
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

results = sp.artist_top_tracks(lz_uri)

for track in results['tracks'][:10]:
    print('track    : ' + track['name'])
    print('audio    : ' + track['preview_url'])
    print('cover art: ' + track['album']['images'][0]['url'])

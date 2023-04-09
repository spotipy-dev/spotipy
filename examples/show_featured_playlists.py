# shows artist info for a URN or URL

import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

response = sp.featured_playlists()
print(response['message'])

while response:
    playlists = response['playlists']
    for i, item in enumerate(playlists['items']):
        print(playlists['offset'] + i, item['name'])

    response = sp.next(playlists) if playlists['next'] else None

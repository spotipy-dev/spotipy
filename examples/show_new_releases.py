# shows artist info for a URN or URL

import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

response = sp.new_releases()

while response:
    albums = response['albums']
    for i, item in enumerate(albums['items']):
        print(albums['offset'] + i, item['name'])

    response = sp.next(albums) if albums['next'] else None

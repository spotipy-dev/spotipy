import base64
from typing import Union

import requests

from spotipy import Spotify


def get_spotify_playlist(spotify_object: Spotify, playlist_name: str, username: str):
    playlists = spotify_object.user_playlists(username)
    while playlists:
        for item in playlists['items']:
            if item['name'] == playlist_name:
                return item
        playlists = spotify_object.next(playlists)


def get_as_base64(url: Union[str, bytes]) -> str:
    return base64.b64encode(requests.get(url).content).decode("utf-8")

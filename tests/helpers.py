import base64
import requests


def get_spotify_playlist(spotify_object, playlist_name, username):
    playlists = spotify_object.user_playlists(username)
    while playlists:
        for item in playlists['items']:
            if item['name'] == playlist_name:
                return item
        playlists = spotify_object.next(playlists)


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content).decode("utf-8")

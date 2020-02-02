# -*- coding: utf-8 -*-

"""
These tests require user authentication - provide client credentials using the
following environment variables

::

    'SPOTIPY_CLIENT_USERNAME'
    'SPOTIPY_CLIENT_ID'
    'SPOTIPY_CLIENT_SECRET'
    'SPOTIPY_REDIRECT_URI'
"""

from __future__ import print_function

from spotipy import (
    CLIENT_CREDS_ENV_VARS as CCEV,
    prompt_for_user_token,
    Spotify,
    SpotifyException,
)
import os
import sys
import unittest
import warnings
import requests
from pprint import pprint  # noqa


class AuthTestSpotipy(unittest.TestCase):
    """
    These tests require user authentication - provide client credentials using
    the following environment variables

    ::

        'SPOTIPY_CLIENT_USERNAME'
        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
        'SPOTIPY_REDIRECT_URI'
    """

    playlist = "spotify:user:plamere:playlist:2oCEWyyAPbZp9xhVSxZavx"
    playlist_new_id = "spotify:playlist:7GlxpQjjxRjmbb3RP2rDqI"
    four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                   "spotify:track:7IHOIqZUUInxjVkko181PB",
                   "4VrWlk8IQxevMvERoX08iC",
                   "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]

    two_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                  "spotify:track:7IHOIqZUUInxjVkko181PB"]

    other_tracks = ["spotify:track:2wySlB6vMzCbQrRnNGOYKa",
                    "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
                    "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]

    album_ids = ["spotify:album:6kL09DaURb7rAoqqaA51KU",
                 "spotify:album:6RTzC0rDbvagTSJLlY7AKl"]

    bad_id = 'BAD_ID'

    @classmethod
    def setUpClass(self):
        if sys.version_info >= (3, 2):
            # >= Python3.2 only
            warnings.filterwarnings(
                "ignore",
                category=ResourceWarning,  # noqa 
                message="unclosed.*<ssl.SSLSocket.*>")

        missing = list(filter(lambda var: not os.getenv(CCEV[var]), CCEV))

        if missing:
            raise Exception(
                ('Please set the client credentials for the test application'
                 ' using the following environment variables: {}').format(
                    CCEV.values()))

        self.username = os.getenv(CCEV['client_username'])

        self.scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload'
        )

        self.token = prompt_for_user_token(self.username, scope=self.scope)

        self.spotify = Spotify(auth=self.token)

    # Helper
    def get_or_create_spotify_playlist(self, playlist_name):
        playlists = self.spotify.user_playlists(self.username)
        while playlists:
            for item in playlists['items']:
                if item['name'] == playlist_name:
                    return item
            playlists = self.spotify.next(playlists)
        return self.spotify.user_playlist_create(
            self.username, playlist_name)

    # Helper
    def get_as_base64(self, url):
        import base64
        return base64.b64encode(requests.get(url).content).decode("utf-8")

    def test_track_bad_id(self):
        try:
            self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_basic_user_profile(self):
        user = self.spotify.user(self.username)
        self.assertTrue(user['id'] == self.username.lower())

    def test_current_user(self):
        user = self.spotify.current_user()
        self.assertTrue(user['id'] == self.username.lower())

    def test_me(self):
        user = self.spotify.me()
        self.assertTrue(user['id'] == self.username.lower())

    def test_user_playlists(self):
        playlists = self.spotify.user_playlists(self.username, limit=5)
        self.assertTrue('items' in playlists)
        self.assertTrue(len(playlists['items']) == 5)

    def test_user_playlist_tracks(self):
        playlists = self.spotify.user_playlists(self.username, limit=5)
        self.assertTrue('items' in playlists)
        for playlist in playlists['items']:
            user = playlist['owner']['id']
            pid = playlist['id']
            results = self.spotify.user_playlist_tracks(user, pid)
            self.assertTrue(len(results['items']) >= 0)

    def test_current_user_saved_albums(self):
        # List
        albums = self.spotify.current_user_saved_albums()
        self.assertTrue(len(albums['items']) > 1)

        # Add
        self.spotify.current_user_saved_albums_add(self.album_ids)

        # Contains
        self.assertTrue(
            self.spotify.current_user_saved_albums_contains(
                self.album_ids) == [
                True, True])

        # Remove
        self.spotify.current_user_saved_albums_delete(self.album_ids)
        albums = self.spotify.current_user_saved_albums()
        self.assertTrue(len(albums['items']) > 1)

    def test_current_user_playlists(self):
        playlists = self.spotify.current_user_playlists(limit=10)
        self.assertTrue('items' in playlists)
        self.assertTrue(len(playlists['items']) == 10)

    def test_user_playlist_follow(self):
        self.spotify.user_playlist_follow_playlist(
            'plamere', '4erXB04MxwRAVqcUEpu30O')
        follows = self.spotify.user_playlist_is_following(
            'plamere', '4erXB04MxwRAVqcUEpu30O', [
                self.spotify.current_user()['id']])

        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertTrue(follows[0], 'is following')
        self.spotify.user_playlist_unfollow(
            'plamere', '4erXB04MxwRAVqcUEpu30O')

        follows = self.spotify.user_playlist_is_following(
            'plamere', '4erXB04MxwRAVqcUEpu30O', [
                self.spotify.current_user()['id']])
        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertFalse(follows[0], 'is no longer following')

    def test_current_user_saved_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        self.assertTrue(len(tracks['items']) > 0)

    def test_current_user_save_and_unsave_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        total = tracks['total']
        self.spotify.current_user_saved_tracks_add(self.four_tracks)

        tracks = self.spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertTrue(new_total - total == len(self.four_tracks))

        tracks = self.spotify.current_user_saved_tracks_delete(
            self.four_tracks)
        tracks = self.spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertTrue(new_total == total)

    def test_categories(self):
        response = self.spotify.categories()
        self.assertTrue(len(response['categories']) > 0)

    def test_category_playlists(self):
        response = self.spotify.categories()
        for cat in response['categories']['items']:
            cat_id = cat['id']
            response = self.spotify.category_playlists(category_id=cat_id)
            if len(response['playlists']["items"]) > 0:
                break
        self.assertTrue(True)

    def test_new_releases(self):
        response = self.spotify.new_releases()
        self.assertTrue(len(response['albums']) > 0)

    def test_featured_releases(self):
        response = self.spotify.featured_playlists()
        self.assertTrue(len(response['playlists']) > 0)

    def test_current_user_follows(self):
        response = self.spotify.current_user_followed_artists()
        artists = response['artists']
        self.assertTrue(len(artists['items']) > 0)

    def test_current_user_top_tracks(self):
        response = self.spotify.current_user_top_tracks()
        items = response['items']
        self.assertTrue(len(items) > 0)

    def test_current_user_top_artists(self):
        response = self.spotify.current_user_top_artists()
        items = response['items']
        self.assertTrue(len(items) > 0)

    def test_current_user_recently_played(self):
        # No cursor
        res = self.spotify.current_user_recently_played()
        self.assertTrue(len(res['items']) <= 50)
        played_at = res['items'][0]['played_at']

        # Using `before` gives tracks played before
        res = self.spotify.current_user_recently_played(
            before=res['cursors']['after'])
        self.assertTrue(len(res['items']) <= 50)
        self.assertTrue(res['items'][0]['played_at'] < played_at)
        played_at = res['items'][0]['played_at']

        # Using `after` gives tracks played after
        res = self.spotify.current_user_recently_played(
            after=res['cursors']['before'])
        self.assertTrue(len(res['items']) <= 50)
        self.assertTrue(res['items'][0]['played_at'] > played_at)

    def test_user_playlist_ops(self):
        sp = self.spotify
        # create empty playlist
        playlist = self.get_or_create_spotify_playlist(
            'spotipy-testing-playlist-1')
        playlist_id = playlist['id']

        # remove all tracks from it
        sp.user_playlist_replace_tracks(
            self.username, playlist_id, [])
        playlist = sp.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 0)
        self.assertTrue(len(playlist['tracks']['items']) == 0)

        # add tracks to it
        sp.user_playlist_add_tracks(
            self.username, playlist_id, self.four_tracks)
        playlist = sp.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 4)
        self.assertTrue(len(playlist['tracks']['items']) == 4)

        # remove two tracks from it

        sp.user_playlist_remove_all_occurrences_of_tracks(self.username,
                                                          playlist_id,
                                                          self.two_tracks)
        playlist = sp.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 2)
        self.assertTrue(len(playlist['tracks']['items']) == 2)

        # replace with 3 other tracks
        sp.user_playlist_replace_tracks(self.username,
                                        playlist_id,
                                        self.other_tracks)
        playlist = sp.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 3)
        self.assertTrue(len(playlist['tracks']['items']) == 3)

    def test_playlist(self):
        # New playlist ID
        pl = self.spotify.playlist(self.playlist_new_id)
        self.assertTrue(pl["tracks"]["total"] > 0)

        # Old playlist ID
        pl = self.spotify.playlist(self.playlist)
        self.assertTrue(pl["tracks"]["total"] > 0)

    def test_playlist_tracks(self):
        # New playlist ID
        pl = self.spotify.playlist_tracks(self.playlist_new_id, limit=2)
        self.assertTrue(len(pl["items"]) == 2)
        self.assertTrue(pl["total"] > 0)

        # Old playlist ID
        pl = self.spotify.playlist_tracks(self.playlist, limit=2)
        self.assertTrue(len(pl["items"]) == 2)
        self.assertTrue(pl["total"] > 0)

    def test_playlist_upload_cover_image(self):
        pl1 = self.get_or_create_spotify_playlist('spotipy-testing-playlist-1')
        plid = pl1['uri']
        old_b64 = pl1['images'][0]['url']

        # Upload random dog image
        r = requests.get('https://dog.ceo/api/breeds/image/random')
        dog_base64 = self.get_as_base64(r.json()['message'])
        self.spotify.playlist_upload_cover_image(plid, dog_base64)

        # Image must be different
        pl1 = self.spotify.playlist(plid)
        new_b64 = self.get_as_base64(pl1['images'][0]['url'])
        self.assertTrue(old_b64 != new_b64)

    def test_playlist_cover_image(self):
        pl = self.get_or_create_spotify_playlist('spotipy-testing-playlist-1')
        plid = pl['uri']
        res = self.spotify.playlist_cover_image(plid)

        self.assertTrue(len(res) > 0)
        first_image = res[0]
        self.assertTrue('width' in first_image)
        self.assertTrue('height' in first_image)
        self.assertTrue('url' in first_image)

    def test_user_follows_and_unfollows_artist(self):
        # Initially follows 1 artist
        res = self.spotify.current_user_followed_artists()
        self.assertTrue(res['artists']['total'] == 1)

        # Follow 2 more artists
        artists = ["6DPYiyq5kWVQS4RGwxzPC7", "0NbfKEOTQCcwd6o7wSDOHI"]
        self.spotify.user_follow_artists(artists)
        res = self.spotify.current_user_followed_artists()
        self.assertTrue(res['artists']['total'] == 3)

        # Unfollow these 2 artists
        self.spotify.user_unfollow_artists(artists)
        res = self.spotify.current_user_followed_artists()
        self.assertTrue(res['artists']['total'] == 1)

    def test_user_follows_and_unfollows_user(self):
        # TODO improve after implementing `me/following/contains`
        users = ["11111204", "xlqeojt6n7on0j7coh9go8ifd"]

        # Follow 2 more users
        self.spotify.user_follow_users(users)

        # Unfollow these 2 users
        self.spotify.user_unfollow_users(users)

    def test_deprecated_starred(self):
        pl = self.spotify.user_playlist(self.username)
        self.assertTrue(pl["tracks"] is None)
        self.assertTrue(pl["owner"] is None)

    def test_deprecated_user_playlist(self):
        # Test without user due to change from
        # https://developer.spotify.com/community/news/2018/06/12/changes-to-playlist-uris/
        pl = self.spotify.user_playlist(None, self.playlist)
        self.assertTrue(pl["tracks"]["total"] > 0)

    def test_deprecated_user_playlis(self):
        # Test without user due to change from
        # https://developer.spotify.com/community/news/2018/06/12/changes-to-playlist-uris/
        pl = self.spotify.user_playlist_tracks(None, self.playlist, limit=2)
        self.assertTrue(len(pl["items"]) == 2)
        self.assertTrue(pl["total"] > 0)

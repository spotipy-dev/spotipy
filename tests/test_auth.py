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

import os
import pprint
import sys
import unittest

import simplejson as json

sys.path.insert(0, os.path.abspath(os.pardir))

from spotipy import (
    CLIENT_CREDS_ENV_VARS as CCEV,
    prompt_for_user_token,
    Spotify,
    SpotifyException,
)


class AuthTestSpotipy(unittest.TestCase):
    """
    These tests require user authentication - provide client credentials using the
    following environment variables

    ::

        'SPOTIPY_CLIENT_USERNAME'
        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
        'SPOTIPY_REDIRECT_URI'
    """

    playlist = "spotify:user:plamere:playlist:2oCEWyyAPbZp9xhVSxZavx"
    four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp", 
                "spotify:track:7IHOIqZUUInxjVkko181PB",
                "4VrWlk8IQxevMvERoX08iC", 
                "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]

    two_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp", 
                "spotify:track:7IHOIqZUUInxjVkko181PB"]

    other_tracks=["spotify:track:2wySlB6vMzCbQrRnNGOYKa", 
            "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
            "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]

    bad_id = 'BAD_ID'

    @classmethod
    def setUpClass(self):

        missing = filter(lambda var: not os.getenv(CCEV[var]), CCEV)

        if missing:
            raise Exception('Please set the client credentials for the test application using the following environment variables: {}'.format(CCEV.values()))

        self.username = os.getenv(CCEV['client_username'])

        self.scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read'
        )

        self.token = prompt_for_user_token(self.username, scope=self.scope)

        self.spotify = Spotify(auth=self.token)

    def test_track_bad_id(self):
        try:
            track = self.spotify.track(self.bad_id)
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

    def user_playlist_tracks(self, user, playlist_id = None, fields=None, 
        limit=100, offset=0):

        # known API issue currently causes this test to fail
        # the issue is that the API doesn't currently respect the
        # limit paramter

        self.assertTrue(len(playlists['items']) == 5)

    def test_current_user_saved_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        self.assertTrue(len(tracks['items']) > 0)

    def test_current_user_saved_albums(self):
        albums = self.spotify.current_user_saved_albums()
        self.assertTrue(len(albums['items']) > 0)

    def test_current_user_playlists(self):
        playlists = self.spotify.current_user_playlists(limit=10)
        self.assertTrue('items' in playlists)
        self.assertTrue(len(playlists['items']) == 10)

    def test_user_playlist_follow(self):
        self.spotify.user_playlist_follow_playlist('plamere', '4erXB04MxwRAVqcUEpu30O')
        follows = self.spotify.user_playlist_is_following('plamere', '4erXB04MxwRAVqcUEpu30O', [self.spotify.current_user()['id']])

        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertTrue(follows[0], 'is following')
        self.spotify.user_playlist_unfollow('plamere', '4erXB04MxwRAVqcUEpu30O')

        follows = self.spotify.user_playlist_is_following('plamere', '4erXB04MxwRAVqcUEpu30O', [self.spotify.current_user()['id']])
        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertFalse(follows[0], 'is no longer following')


    def test_current_user_save_and_unsave_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        total = tracks['total']

        self.spotify.current_user_saved_tracks_add(self.four_tracks)

        tracks = self.spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertTrue(new_total - total == len(self.four_tracks))

        tracks = self.spotify.current_user_saved_tracks_delete(self.four_tracks)
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
            self.assertTrue(len(response['playlists']["items"]) > 0)
    
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

    def get_or_create_spotify_playlist(self, playlist_name):
        playlists = self.spotify.user_playlists(self.username)
        while playlists:
            for item in playlists['items']:
                if item['name'] == playlist_name:
                    return item['id']
            playlists = self.spotify.next(playlists)
        playlist = self.spotify.user_playlist_create(self.username, playlist_name)
        playlist_id = playlist['uri']
        return playlist_id

    def test_user_playlist_ops(self):
        # create empty playlist
        playlist_id = self.get_or_create_spotify_playlist('spotipy-testing-playlist-1')

        # remove all tracks from it

        self.spotify.user_playlist_replace_tracks(self.username, playlist_id,[])

        playlist = self.spotify.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 0)
        self.assertTrue(len(playlist['tracks']['items']) == 0)

        # add tracks to it

        self.spotify.user_playlist_add_tracks(self.username, playlist_id, self.four_tracks)
        playlist = self.spotify.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 4)
        self.assertTrue(len(playlist['tracks']['items']) == 4)

        # remove two tracks from it

        self.spotify.user_playlist_remove_all_occurrences_of_tracks (self.username, 
                    playlist_id, self.two_tracks)

        playlist = self.spotify.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 2)
        self.assertTrue(len(playlist['tracks']['items']) == 2)

        # replace with 3 other tracks
        self.spotify.user_playlist_replace_tracks(self.username, 
            playlist_id, self.other_tracks)

        playlist = self.spotify.user_playlist(self.username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 3)
        self.assertTrue(len(playlist['tracks']['items']) == 3)

if __name__ == '__main__':

    unittest.main()

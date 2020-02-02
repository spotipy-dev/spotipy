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

from spotipy import (
    Spotify,
    SpotifyClientCredentials,
    SpotifyException
)
import spotipy
import unittest
import requests


class AuthTestSpotipy(unittest.TestCase):
    """
    These tests require client authentication - provide client credentials
    using the following environment variables

    ::

        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
    """

    playlist = "spotify:user:plamere:playlist:2oCEWyyAPbZp9xhVSxZavx"
    four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                   "spotify:track:7IHOIqZUUInxjVkko181PB",
                   "4VrWlk8IQxevMvERoX08iC",
                   "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]

    two_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                  "spotify:track:7IHOIqZUUInxjVkko181PB"]

    other_tracks = ["spotify:track:2wySlB6vMzCbQrRnNGOYKa",
                    "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
                    "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]

    bad_id = 'BAD_ID'

    creep_urn = 'spotify:track:3HfB5hBU0dmBt8T0iCmH42'
    creep_id = '3HfB5hBU0dmBt8T0iCmH42'
    creep_url = 'http://open.spotify.com/track/3HfB5hBU0dmBt8T0iCmH42'
    el_scorcho_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'
    el_scorcho_bad_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQK'
    pinkerton_urn = 'spotify:album:04xe676vyiTeYNXw15o9jT'
    weezer_urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
    pablo_honey_urn = 'spotify:album:6AZv3m27uyRxi8KyJSfUxL'
    radiohead_urn = 'spotify:artist:4Z8W4fKeB5YxbusRsdQVPb'
    angeles_haydn_urn = 'spotify:album:1vAbqAeuJVWNAe7UR00bdM'

    @classmethod
    def setUpClass(self):
        self.spotify = Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.spotify.trace = False

    def test_audio_analysis(self):
        result = self.spotify.audio_analysis(self.four_tracks[0])
        assert('beats' in result)

    def test_audio_features(self):
        results = self.spotify.audio_features(self.four_tracks)
        self.assertTrue(len(results) == len(self.four_tracks))
        for track in results:
            assert('speechiness' in track)

    def test_audio_features_with_bad_track(self):
        bad_tracks = []
        bad_tracks = ['spotify:track:bad']
        input = self.four_tracks + bad_tracks
        results = self.spotify.audio_features(input)
        self.assertTrue(len(results) == len(input))
        for track in results[:-1]:
            if track is not None:
                assert('speechiness' in track)
        self.assertTrue(results[-1] is None)

    def test_recommendations(self):
        results = self.spotify.recommendations(
            seed_tracks=self.four_tracks,
            min_danceability=0,
            max_loudness=0,
            target_popularity=50)
        self.assertTrue(len(results['tracks']) == 20)

    def test_artist_urn(self):
        artist = self.spotify.artist(self.radiohead_urn)
        self.assertTrue(artist['name'] == 'Radiohead')

    def test_artists(self):
        results = self.spotify.artists([self.weezer_urn, self.radiohead_urn])
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 2)

    def test_album_urn(self):
        album = self.spotify.album(self.pinkerton_urn)
        self.assertTrue(album['name'] == 'Pinkerton')

    def test_album_tracks(self):
        results = self.spotify.album_tracks(self.pinkerton_urn)
        self.assertTrue(len(results['items']) == 10)

    def test_album_tracks_many(self):
        results = self.spotify.album_tracks(self.angeles_haydn_urn)
        tracks = results['items']
        total, received = results['total'], len(tracks)
        while received < total:
            results = self.spotify.album_tracks(
                self.angeles_haydn_urn, offset=received)
            tracks.extend(results['items'])
            received = len(tracks)

        self.assertEqual(received, total)

    def test_albums(self):
        results = self.spotify.albums(
            [self.pinkerton_urn, self.pablo_honey_urn])
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']) == 2)

    def test_track_urn(self):
        track = self.spotify.track(self.creep_urn)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_id(self):
        track = self.spotify.track(self.creep_id)
        self.assertTrue(track['name'] == 'Creep')
        self.assertTrue(track['popularity'] > 0)

    def test_track_url(self):
        track = self.spotify.track(self.creep_url)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_bad_urn(self):
        try:
            self.spotify.track(self.el_scorcho_bad_urn)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_tracks(self):
        results = self.spotify.tracks([self.creep_url, self.el_scorcho_urn])
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 2)

    def test_artist_top_tracks(self):
        results = self.spotify.artist_top_tracks(self.weezer_urn)
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 10)

    def test_artist_related_artists(self):
        results = self.spotify.artist_related_artists(self.weezer_urn)
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 20)
        for artist in results['artists']:
            if artist['name'] == 'Jimmy Eat World':
                found = True
        self.assertTrue(found)

    def test_artist_search(self):
        results = self.spotify.search(q='weezer', type='artist')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_search_with_market(self):
        results = self.spotify.search(q='weezer', type='artist', market='GB')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_albums(self):
        results = self.spotify.artist_albums(self.weezer_urn)
        self.assertTrue('items' in results)
        self.assertTrue(len(results['items']) > 0)

        found = False
        for album in results['items']:
            if album['name'] == 'Hurley':
                found = True

        self.assertTrue(found)

    def test_search_timeout(self):
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            requests_timeout=.01)

        try:
            sp.search(q='my*', type='track')
            self.assertTrue(False, 'unexpected search timeout')
        except requests.exceptions.Timeout:
            self.assertTrue(True, 'expected search timeout')

    def test_album_search(self):
        results = self.spotify.search(q='weezer pinkerton', type='album')
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']['items']) > 0)
        self.assertTrue(results['albums']['items'][0]
                        ['name'].find('Pinkerton') >= 0)

    def test_track_search(self):
        results = self.spotify.search(q='el scorcho weezer', type='track')
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']['items']) > 0)
        self.assertTrue(results['tracks']['items'][0]['name'] == 'El Scorcho')

    def test_user(self):
        user = self.spotify.user(user='plamere')
        self.assertTrue(user['uri'] == 'spotify:user:plamere')

    def test_track_bad_id(self):
        try:
            self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_unauthenticated_post_fails(self):
        with self.assertRaises(SpotifyException) as cm:
            self.spotify.user_playlist_create(
                "spotify", "Best hits of the 90s")
        self.assertTrue(cm.exception.http_status == 401 or
                        cm.exception.http_status == 403)

    def test_custom_requests_session(self):
        sess = requests.Session()
        sess.headers["user-agent"] = "spotipy-test"
        with_custom_session = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(),
            requests_session=sess)
        self.assertTrue(
            with_custom_session.user(
                user="akx")["uri"] == "spotify:user:akx")
        sess.close()

    def test_force_no_requests_session(self):
        from requests import Session
        with_no_session = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(),
            requests_session=False)
        self.assertFalse(isinstance(with_no_session._session, Session))
        self.assertTrue(with_no_session.user(user="akx")
                        ["uri"] == "spotify:user:akx")

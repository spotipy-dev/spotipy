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

import os
import pprint
import sys
import unittest

import simplejson as json

sys.path.insert(0, os.path.abspath(os.pardir))

from spotipy import (
    Spotify,
    SpotifyClientCredentials,
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
        self.spotify = Spotify(client_credentials_manager=SpotifyClientCredentials())
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
            if track != None:
                assert('speechiness' in track)
        self.assertTrue(results[-1] == None)

    def test_recommendations(self):
        results = self.spotify.recommendations(seed_tracks=self.four_tracks, min_danceability=0, max_loudness=0, target_popularity=50)
        self.assertTrue(len(results['tracks']) == 20)


if __name__ == '__main__':

    unittest.main()

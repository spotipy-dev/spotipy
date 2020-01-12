# -*- coding: utf-8 -*-

""" Client Credentials Requests Tests """

from spotipy import (
    Spotify,
    SpotifyClientCredentials,
)
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.pardir))


class ClientCredentialsTestSpotipy(unittest.TestCase):
    """
    These tests require user authentication - provide client credentials using
    the following environment variables

    ::

        'SPOTIPY_CLIENT_USERNAME'
        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
        'SPOTIPY_REDIRECT_URI'
    """

    @classmethod
    def setUpClass(self):
        self.spotify = Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.spotify.trace = False

    muse_urn = 'spotify:artist:12Chz98pHFMPJEknJQMWvI'

    def test_request_with_token(self):
        artist = self.spotify.artist(self.muse_urn)
        self.assertTrue(artist['name'] == 'Muse')


if __name__ == '__main__':
    unittest.main()

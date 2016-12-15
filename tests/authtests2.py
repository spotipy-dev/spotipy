# -*- coding: latin-1 -*-

import spotipy
from  spotipy import util
import unittest
import pprint
import sys
import simplejson as json
from spotipy.oauth2 import SpotifyClientCredentials

'''
    Since these tests require authentication they are maintained
    separately from the other tests.

    These tests try to be benign and leave your collection and
    playlists in a relatively stable state.
'''

class AuthTestSpotipy(unittest.TestCase):
    '''
        These tests require user authentication
    '''

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


    def test_audio_analysis(self):
        result = spotify.audio_analysis(self.four_tracks[0])
        assert('beats' in result)

    def test_audio_features(self):
        results = spotify.audio_features(self.four_tracks)
        self.assertTrue(len(results) == len(self.four_tracks))
        for track in results:
            assert('speechiness' in track)

    def test_audio_features_with_bad_track(self):
        bad_tracks = []
        bad_tracks = ['spotify:track:bad']
        input = self.four_tracks + bad_tracks
        results = spotify.audio_features(input)
        self.assertTrue(len(results) == len(input))
        for track in results[:-1]:
            if track != None:
                assert('speechiness' in track)
        self.assertTrue(results[-1] == None)

    def test_recommendations(self):
        results = spotify.recommendations(seed_tracks=self.four_tracks, min_danceability=0, max_loudness=0, target_popularity=50)
        self.assertTrue(len(results['tracks']) == 20)


if __name__ == '__main__':
    client_credentials_manager = SpotifyClientCredentials()
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    spotify.trace = False
    unittest.main()

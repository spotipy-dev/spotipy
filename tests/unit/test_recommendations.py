import unittest
import spotipy

# -*- coding: utf-8 -*-

from spotipy import (
    Spotify,
    SpotifyClientCredentials,
    SpotifyException
)
import spotipy
import unittest
import requests

class SpotipyLibraryTests(unittest.TestCase):
    
    def setUp(self):
        self.spotify = Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.spotify.trace = False

    # *************************************
    # Used to test recommendations function for the 
    # spotipy.

    # Link to documentation:
    # https://spotipy.readthedocs.io/en/2.22.1/#:~:text=recommendations(seed_artists,targeting%20on%20results.

    # *************************************

    def test_invalid_seed_artist(self):
        #Test recommendations function using invalid seed artist
        with self.assertRaises(SpotifyException):            
            self.spotify.recommendations(seed_artists="115111511151115111")

    def test_invalid_seed_genre(self):
        #Test recommendations function using invalid seed genre
        with self.assertRaises(SpotifyException):
            self.spotify.recommendations(seed_genre="115111511151115111")

    def test_invalid_seed_track(self):
        #Test recommendations function using invalid seed track
        with self.assertRaises(SpotifyException):        
            self.spotify.recommendations(seed_genre="115111511151115111")


    def test_invalid_limit(self):
        #Test recommendations function using invalid limit
        with self.assertRaises(SpotifyException):
            self.spotify.recommendations(limit=101)

    def test_invalid_country(self):
        #Test recommendations function using invalid country
        with self.assertRaises(SpotifyException):
            self.spotify.recommendations(country="USA")

if __name__ == '__main__':
    unittest.main()

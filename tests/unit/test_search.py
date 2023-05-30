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
    # Used to test search function for the 
    # spotipy.

    # Link to documentation:
    # https://spotipy.readthedocs.io/en/2.22.1/#:~:text=search(q%2C,from_token.

    # *************************************

    def test_invalid_artist(self):
        #Test search using invalid artist name
        result = self.spotify.search(q='artist:Thisisnotavalidartist')

        #should return empty array of items
        self.assertEqual(result['tracks']['items'], [])

        #should return total as 0
        self.assertEqual(result['tracks']['total'], 0)

    def test_invalid_limit(self):
        #Test search using invalid limit
        with self.assertRaises(SpotifyException):
            self.spotify.search(q='artist:Taylor Swift', limit=105)

    def test_invalid_type(self):
        #Test search using invalid type
        with self.assertRaises(SpotifyException):
            self.spotify.search(q='artist:Taylor Swift', type='invalid')
    
    def test_empty_query(self):
        #Test search using empty string in query
        with self.assertRaises(SpotifyException):
            self.spotify.search(q="")

    def test_invalid_market_code(self):
        #Test search using invalid market code
        with self.assertRaises(SpotifyException):
            self.spotify.search(q="artist:Taylor Swift", market="USA")

if __name__ == '__main__':
    unittest.main()

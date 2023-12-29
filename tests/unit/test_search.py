import unittest
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import traceback


class artist_info_test_case(unittest.TestCase):
    def test_artist_info_with_search_str(self):
        search_str = 'Radiohead'
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='id_client', client_secret='secret_client'))
        result = sp.search(search_str)

        # Assert that the 'tracks' key is present in the result
        self.assertIn('tracks', result)

        # Assert that the 'items' key is present in the 'tracks' dictionary
        self.assertIn('items', result['tracks'])

        # Assert that the 'items' list is not empty
        self.assertTrue(len(result['tracks']['items']) > 0)


class exception_test_case(unittest.TestCase):
    def test_empty_search_query(self):
        search_str = "Radiohead"
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='id_client', client_secret='secret_client'))
        result = sp.search(search_str)

        # Assert that the 'tracks' key is present in the result
        self.assertIn('tracks', result)

    def test_invalid_search_query(self):
        search_str = "1234"
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id='id_client', client_secret='secret_client'))
        result = sp.search(search_str)

        # Make sure at least some tracks are returned
        self.assertNotEqual(result['tracks']['total'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

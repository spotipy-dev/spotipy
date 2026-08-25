import unittest
import unittest.mock as mock

from spotipy import Spotify


class SearchQueryLengthTest(unittest.TestCase):

    def setUp(self):
        self.spotify = Spotify(auth="TOKEN")

    @mock.patch.object(Spotify, "_internal_call", return_value={})
    def test_long_query_warns(self, _internal_call):
        query = "a" * (Spotify.max_search_query_length + 1)
        with self.assertLogs("spotipy.client", level="WARNING") as logs:
            self.spotify.search(query)
        self.assertTrue(
            any("character limit" in message or "character" in message
                for message in logs.output)
        )

    @mock.patch.object(Spotify, "_internal_call", return_value={})
    def test_short_query_does_not_warn(self, _internal_call):
        query = "a" * Spotify.max_search_query_length
        logger = "spotipy.client"
        with self.assertRaises(AssertionError):
            with self.assertLogs(logger, level="WARNING"):
                self.spotify.search(query)


if __name__ == "__main__":
    unittest.main()

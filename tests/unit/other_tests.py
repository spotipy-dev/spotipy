# Unit testing some of the methods of the spotipy.client.Spotify class
# This is not an exhaustive test suite
# Note: this test suite currently requires a user to be authenticated (to be fixed in a future update)

# Import the necessary packages
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import unittest

# Set up authentication credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope="playlist-modify-public,user-top-read,user-library-read,user-read-recently-played,user-follow-read,user-follow-modify"))
# get the user's username
username = sp.me()['id']


def _delete_playlist(id):
    """
    Delete a playlist by ID
    :param id: the ID of the playlist to delete
    """
    sp.current_user_unfollow_playlist(id)


class TestSpotifyClient(unittest.TestCase):
    def test_get_user_top_tracks(self):
        """
        Test that the user's top tracks are returned.
        Checks that the number of tracks returned is equal to the limit.
        Conditions:
        - the user has at least 5 top tracks
        """
        top_tracks = sp.current_user_top_tracks(
            limit=5, time_range='long_term')
        self.assertEqual(len(top_tracks['items']), 5)

    def test_get_user_saved_tracks(self):
        """
        Test that the user's liked tracks are returned.
        Checks that the number of tracks returned is equal to the limit.
        Conditions:
        - the user has at least 5 liked tracks
        """
        liked_tracks = sp.current_user_saved_tracks(limit=5)
        self.assertEqual(len(liked_tracks['items']), 5)

    def test_get_user_recently_played_tracks(self):
        """
        Test that the user's listening history is returned.
        Checks that the number of tracks returned is equal to the limit.
        Conditions:
        - the user has at least 5 tracks in their listening history
        """
        history = sp.current_user_recently_played(limit=5)
        self.assertEqual(len(history['items']), 5)

    def test_get_user_playlists(self):
        """
        Test that the user's playlists are returned.
        Checks that the number of playlists returned is greater than or equal to 0.
        """
        playlists = sp.current_user_playlists()
        self.assertGreaterEqual(len(playlists['items']), 0)

    def test_create_playlist(self):
        """
        Test that a playlist is created.
        Checks that the added playlist name and description are correct.
        """
        playlist_name = "test_playlist"
        playlist_description = "test_description"
        playlist = sp.user_playlist_create(
            user=username, name=playlist_name, public=True, collaborative=False, description=playlist_description)
        self.assertEqual(playlist['name'], playlist_name)
        self.assertEqual(playlist['description'], playlist_description)
        _delete_playlist(playlist['id'])

    def test_add_tracks_to_playlist(self):
        """
        Test that tracks are added to a playlist.
        Checks that the number of tracks in the playlist is equal to the number of tracks added.
        """
        playlist_name = "test_playlist"
        playlist_description = "test_description"
        playlist = sp.user_playlist_create(
            user=username, name=playlist_name, public=True, collaborative=False, description=playlist_description)
        tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')
        track_ids = [track['id'] for track in tracks['items']]
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)
        playlist_tracks = sp.playlist_items(playlist_id=playlist['id'])
        self.assertEqual(len(playlist_tracks['items']), 5)
        _delete_playlist(playlist['id'])

    def test_remove_tracks_from_playlist(self):
        """
        Test that tracks are removed from a playlist.
        Checks that the number of tracks in the playlist is equal to 0 after removing everything.
        """
        playlist_name = "test_playlist"
        playlist_description = "test_description"
        playlist = sp.user_playlist_create(
            user=username, name=playlist_name, public=True, collaborative=False, description=playlist_description)
        tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')
        track_ids = [track['id'] for track in tracks['items']]
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)
        playlist_tracks = sp.playlist_items(playlist_id=playlist['id'])
        self.assertEqual(len(playlist_tracks['items']), 5)
        sp.playlist_remove_all_occurrences_of_items(
            playlist_id=playlist['id'], items=track_ids)
        playlist_tracks = sp.playlist_items(playlist_id=playlist['id'])
        self.assertEqual(len(playlist_tracks['items']), 0)
        _delete_playlist(playlist['id'])

    def test_user_follow_artist(self):
        """
        Test that an artist is followed correctly.
        Checks that the artist is in the user's followed artists list.
        Conditions:
        - the user is not already following any artists
        """
        artist_id = '3WrFJ7ztbogyGnTHbHJFl2'
        sp.user_follow_artists([artist_id])
        followed_artists = sp.current_user_followed_artists(limit=1)
        self.assertEqual(
            followed_artists['artists']['items'][0]['id'], artist_id)

    def test_user_unfollow_artist(self):
        """
        Test that an artist is unfollowed correctly.
        Checks that the artist is not in the user's followed artists list.
        Conditions:
        - the user is following the artist (see test_user_follow_artist))
        """
        artist_id = '3WrFJ7ztbogyGnTHbHJFl2'
        sp.user_unfollow_artists([artist_id])
        followed_artists = sp.current_user_followed_artists(limit=1)
        self.assertEqual(len(followed_artists['artists']['items']), 0)

    def test_search_for_one_track(self):
        """
        Test that a track is found correctly.
        Checks that the track name is correct.
        """
        tracks = sp.search(q='track:All I Want for Christmas Is You',
                           type='track', limit=1)
        self.assertEqual(tracks['tracks']['items'][0]['name'],
                         'All I Want for Christmas Is You')

    def test_search_for_one_album(self):
        """
        Test that an album is found correctly.
        Checks that the album name is correct.
        """
        albums = sp.search(q='album:72 Seasons',
                           type='album', limit=1)
        self.assertEqual(albums['albums']['items'][0]['name'],
                         '72 Seasons')

    def test_search_for_one_artist(self):
        """
        Test that an artist is found correctly.
        Checks that the artist name is correct.
        """
        artists = sp.search(q='artist:Taylor Swift',
                            type='artist', limit=1)
        self.assertEqual(artists['artists']['items'][0]['name'],
                         'Taylor Swift')


if __name__ == "__main__":
    unittest.main()

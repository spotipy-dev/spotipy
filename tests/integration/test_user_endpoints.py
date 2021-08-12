import os

from spotipy import (
    CLIENT_CREDS_ENV_VARS as CCEV,
    prompt_for_user_token,
    Spotify,
    SpotifyException,
    SpotifyImplicitGrant,
    SpotifyPKCE
)
import unittest
from tests import helpers


class SpotipyPlaylistApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                           "spotify:track:7IHOIqZUUInxjVkko181PB",
                           "4VrWlk8IQxevMvERoX08iC",
                           "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]
        cls.other_tracks = ["spotify:track:2wySlB6vMzCbQrRnNGOYKa",
                            "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
                            "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]
        cls.username = os.getenv(CCEV['client_username'])

        # be wary here, episodes sometimes go away forever
        # which could cause tests that rely on four_episodes
        # to fail

        cls.four_episodes = [
            "spotify:episode:7f9e73vfXKRqR6uCggK2Xy",
            "spotify:episode:4wA1RLFNOWCJ8iprngXmM0",
            "spotify:episode:32vhLjJjT7m3f9DFCJUCVZ",
            "spotify:episode:7cRcsGYYRUFo1OF3RgRzdx",
        ]

        scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload '
            'user-read-playback-state'
        )

        token = prompt_for_user_token(cls.username, scope=scope)

        cls.spotify = Spotify(auth=token)
        cls.spotify_no_retry = Spotify(auth=token, retries=0)
        cls.new_playlist_name = 'spotipy-playlist-test'
        cls.new_playlist = helpers.get_spotify_playlist(
            cls.spotify, cls.new_playlist_name, cls.username) or \
            cls.spotify.user_playlist_create(cls.username, cls.new_playlist_name)
        cls.new_playlist_uri = cls.new_playlist['uri']

    @classmethod
    def tearDownClass(cls):
        cls.spotify.current_user_unfollow_playlist(cls.new_playlist['id'])

    def test_user_playlists(self):
        playlists = self.spotify.user_playlists(self.username, limit=5)
        self.assertTrue('items' in playlists)
        self.assertGreaterEqual(len(playlists['items']), 1)

    def test_playlist_items(self):
        playlists = self.spotify.user_playlists(self.username, limit=5)
        self.assertTrue('items' in playlists)
        for playlist in playlists['items']:
            if playlist['uri'] != self.new_playlist_uri:
                continue
            pid = playlist['id']
            results = self.spotify.playlist_items(pid)
            self.assertEqual(len(results['items']), 0)

    def test_current_user_playlists(self):
        playlists = self.spotify.current_user_playlists(limit=10)
        self.assertTrue('items' in playlists)
        self.assertGreaterEqual(len(playlists['items']), 1)
        self.assertLessEqual(len(playlists['items']), 10)

    def test_current_user_follow_playlist(self):
        playlist_to_follow_id = '4erXB04MxwRAVqcUEpu30O'
        self.spotify.current_user_follow_playlist(playlist_to_follow_id)
        follows = self.spotify.playlist_is_following(
            playlist_to_follow_id, [self.username])

        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertTrue(follows[0], 'is following')
        self.spotify.current_user_unfollow_playlist(playlist_to_follow_id)

        follows = self.spotify.playlist_is_following(
            playlist_to_follow_id, [self.username])
        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertFalse(follows[0], 'is no longer following')

    def test_playlist_replace_items(self):
        # add tracks to playlist
        self.spotify.playlist_add_items(
            self.new_playlist['id'], self.four_tracks)
        playlist = self.spotify.playlist(self.new_playlist['id'])
        self.assertEqual(playlist['tracks']['total'], 4)
        self.assertEqual(len(playlist['tracks']['items']), 4)

        # replace with 3 other tracks
        self.spotify.playlist_replace_items(self.new_playlist['id'],
                                            self.other_tracks)
        playlist = self.spotify.playlist(self.new_playlist['id'])
        self.assertEqual(playlist['tracks']['total'], 3)
        self.assertEqual(len(playlist['tracks']['items']), 3)

        self.spotify.playlist_remove_all_occurrences_of_items(
            playlist['id'], self.other_tracks)
        playlist = self.spotify.playlist(self.new_playlist['id'])
        self.assertEqual(playlist["tracks"]["total"], 0)

    def test_get_playlist_by_id(self):
        pl = self.spotify.playlist(self.new_playlist['id'])
        self.assertEqual(pl["tracks"]["total"], 0)

    def test_max_retries_reached_post(self):
        import concurrent.futures
        max_workers = 100
        total_requests = 500

        def do():
            self.spotify_no_retry.playlist_change_details(
                self.new_playlist['id'], description="test")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_post = (executor.submit(do) for _i in range(1, total_requests))
            for future in concurrent.futures.as_completed(future_to_post):
                try:
                    future.result()
                except Exception as exc:
                    # Test success
                    self.assertIsInstance(exc, SpotifyException)
                    self.assertEqual(exc.http_status, 429)
                    return

        self.fail()

    def test_playlist_add_items(self):
        # add tracks to playlist
        self.spotify.playlist_add_items(
            self.new_playlist['id'], self.other_tracks)
        playlist = self.spotify.playlist_items(self.new_playlist['id'])
        self.assertEqual(playlist['total'], 3)
        self.assertEqual(len(playlist['items']), 3)

        pl = self.spotify.playlist_items(self.new_playlist['id'], limit=2)
        self.assertEqual(len(pl["items"]), 2)

        self.spotify.playlist_remove_all_occurrences_of_items(
            self.new_playlist['id'], self.other_tracks)
        playlist = self.spotify.playlist_items(self.new_playlist['id'])
        self.assertEqual(playlist["total"], 0)

    def test_playlist_add_episodes(self):
        # add episodes to playlist
        self.spotify.playlist_add_items(
            self.new_playlist['id'], self.four_episodes)
        playlist = self.spotify.playlist_items(self.new_playlist['id'])
        self.assertEqual(playlist['total'], 4)
        self.assertEqual(len(playlist['items']), 4)

        pl = self.spotify.playlist_items(self.new_playlist['id'], limit=2)
        self.assertEqual(len(pl["items"]), 2)

        self.spotify.playlist_remove_all_occurrences_of_items(
            self.new_playlist['id'], self.four_episodes)
        playlist = self.spotify.playlist_items(self.new_playlist['id'])
        self.assertEqual(playlist["total"], 0)

    def test_playlist_cover_image(self):
        # From https://dog.ceo/api/breeds/image/random
        small_image = "https://images.dog.ceo/breeds/poodle-toy/n02113624_8936.jpg"
        dog_base64 = helpers.get_as_base64(small_image)
        self.spotify.playlist_upload_cover_image(self.new_playlist_uri, dog_base64)

        res = self.spotify.playlist_cover_image(self.new_playlist_uri)
        self.assertEqual(len(res), 1)
        first_image = res[0]
        self.assertIn('width', first_image)
        self.assertIn('height', first_image)
        self.assertIn('url', first_image)

    def test_large_playlist_cover_image(self):
        # From https://dog.ceo/api/breeds/image/random
        large_image = "https://images.dog.ceo/breeds/pointer-germanlonghair/hans2.jpg"
        dog_base64 = helpers.get_as_base64(large_image)
        try:
            self.spotify.playlist_upload_cover_image(self.new_playlist_uri, dog_base64)
        except Exception as e:
            self.assertIsInstance(e, SpotifyException)
            self.assertEqual(e.http_status, 413)
            return
        self.fail()

    def test_deprecated_starred(self):
        pl = self.spotify.user_playlist(self.username)
        self.assertTrue(pl["tracks"] is None)
        self.assertTrue(pl["owner"] is None)

    def test_deprecated_user_playlist(self):
        # Test without user due to change from
        # https://developer.spotify.com/community/news/2018/06/12/changes-to-playlist-uris/
        pl = self.spotify.user_playlist(None, self.new_playlist['id'])
        self.assertEqual(pl["tracks"]["total"], 0)


class SpotipyLibraryApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                           "spotify:track:7IHOIqZUUInxjVkko181PB",
                           "4VrWlk8IQxevMvERoX08iC",
                           "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]
        cls.album_ids = ["spotify:album:6kL09DaURb7rAoqqaA51KU",
                         "spotify:album:6RTzC0rDbvagTSJLlY7AKl"]
        cls.episode_ids = [
            "spotify:episode:3OEdPEYB69pfXoBrhvQYeC",
            "spotify:episode:5LEFdZ9pYh99wSz7Go2D0g"
        ]
        cls.username = os.getenv(CCEV['client_username'])

        scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload '
            'user-read-playback-state'
        )

        token = prompt_for_user_token(cls.username, scope=scope)

        cls.spotify = Spotify(auth=token)

    def test_track_bad_id(self):
        with self.assertRaises(SpotifyException):
            self.spotify.track('BadID123')

    def test_current_user_saved_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        self.assertGreaterEqual(len(tracks['items']), 0)

    def test_current_user_save_and_unsave_tracks(self):
        tracks = self.spotify.current_user_saved_tracks()
        total = tracks['total']
        self.spotify.current_user_saved_tracks_add(self.four_tracks)

        tracks = self.spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertEqual(new_total - total, len(self.four_tracks))

        self.spotify.current_user_saved_tracks_delete(
            self.four_tracks)
        tracks = self.spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertEqual(new_total, total)

    def test_current_user_saved_albums(self):
        # Add
        self.spotify.current_user_saved_albums_add(self.album_ids)
        albums = self.spotify.current_user_saved_albums()
        self.assertGreaterEqual(len(albums['items']), 2)

        # Contains
        resp = self.spotify.current_user_saved_albums_contains(self.album_ids)
        self.assertEqual(resp, [True, True])

        # Remove
        self.spotify.current_user_saved_albums_delete(self.album_ids)
        resp = self.spotify.current_user_saved_albums_contains(self.album_ids)
        self.assertEqual(resp, [False, False])

    def test_current_user_saved_episodes(self):
        # Add
        self.spotify.current_user_saved_episodes_add(self.episode_ids)
        episodes = self.spotify.current_user_saved_episodes(market="US")
        self.assertGreaterEqual(len(episodes['items']), 2)

        # Contains
        resp = self.spotify.current_user_saved_episodes_contains(self.episode_ids)
        self.assertEqual(resp, [True, True])

        # Remove
        self.spotify.current_user_saved_episodes_delete(self.episode_ids)
        resp = self.spotify.current_user_saved_episodes_contains(self.episode_ids)
        self.assertEqual(resp, [False, False])


class SpotipyUserApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = os.getenv(CCEV['client_username'])

        scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload '
            'user-read-playback-state'
        )

        token = prompt_for_user_token(cls.username, scope=scope)

        cls.spotify = Spotify(auth=token)

    def test_basic_user_profile(self):
        user = self.spotify.user(self.username)
        self.assertEqual(user['id'], self.username.lower())

    def test_current_user(self):
        user = self.spotify.current_user()
        self.assertEqual(user['id'], self.username.lower())

    def test_me(self):
        user = self.spotify.me()
        self.assertTrue(user['id'] == self.username.lower())

    def test_current_user_top_tracks(self):
        response = self.spotify.current_user_top_tracks()
        items = response['items']
        self.assertGreaterEqual(len(items), 0)

    def test_current_user_top_artists(self):
        response = self.spotify.current_user_top_artists()
        items = response['items']
        self.assertGreaterEqual(len(items), 0)


class SpotipyBrowseApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        username = os.getenv(CCEV['client_username'])
        token = prompt_for_user_token(username)
        cls.spotify = Spotify(auth=token)

    def test_category(self):
        response = self.spotify.category('rock')
        self.assertTrue('name' in response)

    def test_categories(self):
        response = self.spotify.categories()
        self.assertGreater(len(response['categories']), 0)

    def test_category_playlists(self):
        response = self.spotify.categories()
        category = 'rock'
        for cat in response['categories']['items']:
            cat_id = cat['id']
            if cat_id == category:
                response = self.spotify.category_playlists(category_id=cat_id)
                self.assertGreater(len(response['playlists']["items"]), 0)

    def test_new_releases(self):
        response = self.spotify.new_releases()
        self.assertGreater(len(response['albums']), 0)

    def test_featured_releases(self):
        response = self.spotify.featured_playlists()
        self.assertGreater(len(response['playlists']), 0)


class SpotipyFollowApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = os.getenv(CCEV['client_username'])

        scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload '
            'user-read-playback-state'
        )

        token = prompt_for_user_token(cls.username, scope=scope)

        cls.spotify = Spotify(auth=token)

    def test_current_user_follows(self):
        response = self.spotify.current_user_followed_artists()
        artists = response['artists']
        self.assertGreaterEqual(len(artists['items']), 0)

    def test_user_follows_and_unfollows_artist(self):
        # Initially follows 1 artist
        current_user_followed_artists = self.spotify.current_user_followed_artists()[
            'artists']['total']

        # Follow 2 more artists
        artists = ["6DPYiyq5kWVQS4RGwxzPC7", "0NbfKEOTQCcwd6o7wSDOHI"]
        self.spotify.user_follow_artists(artists)
        self.assertTrue(all(self.spotify.current_user_following_artists(artists)))

        # Unfollow these 2 artists
        self.spotify.user_unfollow_artists(artists)
        self.assertFalse(any(self.spotify.current_user_following_artists(artists)))
        res = self.spotify.current_user_followed_artists()
        self.assertEqual(res['artists']['total'], current_user_followed_artists)

    def test_user_follows_and_unfollows_user(self):
        users = ["11111204", "xlqeojt6n7on0j7coh9go8ifd"]

        # Follow 2 more users
        self.spotify.user_follow_users(users)
        self.assertTrue(all(self.spotify.current_user_following_users(users)))

        # Unfollow these 2 users
        self.spotify.user_unfollow_users(users)
        self.assertFalse(any(self.spotify.current_user_following_users(users)))


class SpotipyPlayerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = os.getenv(CCEV['client_username'])

        scope = (
            'playlist-modify-public '
            'user-library-read '
            'user-follow-read '
            'user-library-modify '
            'user-read-private '
            'user-top-read '
            'user-follow-modify '
            'user-read-recently-played '
            'ugc-image-upload '
            'user-read-playback-state'
        )

        token = prompt_for_user_token(cls.username, scope=scope)

        cls.spotify = Spotify(auth=token)

    def test_devices(self):
        # No devices playing by default
        res = self.spotify.devices()
        self.assertGreaterEqual(len(res["devices"]), 0)

    def test_current_user_recently_played(self):
        # No cursor
        res = self.spotify.current_user_recently_played()
        self.assertLessEqual(len(res['items']), 50)
        # not much more to test if account is inactive and has no recently played tracks


class SpotipyImplicitGrantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scope = (
            'user-follow-read '
            'user-follow-modify '
        )
        auth_manager = SpotifyImplicitGrant(scope=scope,
                                            cache_path=".cache-implicittest")
        cls.spotify = Spotify(auth_manager=auth_manager)

    def test_current_user(self):
        c_user = self.spotify.current_user()
        user = self.spotify.user(c_user['id'])
        self.assertEqual(c_user['display_name'], user['display_name'])


class SpotifyPKCETests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        scope = (
            'user-follow-read '
            'user-follow-modify '
        )
        auth_manager = SpotifyPKCE(scope=scope, cache_path=".cache-pkcetest")
        cls.spotify = Spotify(auth_manager=auth_manager)

    def test_current_user(self):
        c_user = self.spotify.current_user()
        user = self.spotify.user(c_user['id'])
        self.assertEqual(c_user['display_name'], user['display_name'])

from unittest import TestCase
from spotipy.scope import Scope
from spotipy.oauth2 import SpotifyAuthBase


class SpotipyScopeTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.auth_manager = SpotifyAuthBase(requests_session=True)

    def normalize_scope(self, scope):
        return self.auth_manager._normalize_scope(scope)

    def test_empty_scope(self):
        scopes = set()
        scope_string = Scope.make_string(scopes)

        normalized_scope_string = self.normalize_scope(scopes)
        normalized_scope_string_2 = self.normalize_scope(scope_string)

        self.assertEqual(scope_string, "")
        self.assertEqual(normalized_scope_string, "")
        self.assertEqual(normalized_scope_string_2, "")

        converted_scopes = Scope.from_string(scope_string)
        self.assertEqual(converted_scopes, set())

    def test_scopes(self):
        scopes = {
            Scope.playlist_modify_public,
            Scope.playlist_read_collaborative,
            Scope.user_read_playback_state,
            Scope.ugc_image_upload
        }
        normalized_scope_string = self.normalize_scope(scopes)
        scope_string = Scope.make_string(scopes)
        self.assertEqual(scope_string, normalized_scope_string)

        normalized_scope_string_2 = self.normalize_scope(scope_string)

        converted_scopes = Scope.from_string(scope_string)
        normalized_converted_scope = Scope.from_string(normalized_scope_string)
        normalized_converted_scope_2 = Scope.from_string(normalized_scope_string_2)
        self.assertEqual(scopes, converted_scopes)
        self.assertEqual(scopes, normalized_converted_scope)
        self.assertEqual(scopes, normalized_converted_scope_2)

    def test_single_scope(self):
        scope_string = "user-modify-playback-state"
        scope = Scope(scope_string)
        self.assertEqual(scope, Scope.user_modify_playback_state)
        self.assertEqual(scope_string, scope.value)

    def test_scope_string(self):
        scope_string = (
            "user-read-currently-playing    playlist-read-collaborative,user-library-read "
            "playlist-read-private user-read-email"
        )
        expected_scopes = {
            Scope.user_read_currently_playing,
            Scope.playlist_read_collaborative,
            Scope.user_library_read,
            Scope.playlist_read_private,
            Scope.user_read_email
        }
        parsed_scopes = Scope.from_string(scope_string)
        normalized_scope_string = self.normalize_scope(scope_string)
        normalized_parsed_scopes = Scope.from_string(normalized_scope_string)
        self.assertEqual(parsed_scopes, expected_scopes)
        self.assertEqual(normalized_parsed_scopes, expected_scopes)

    def test_invalid_types(self):

        numbers = [1, 2, 3]
        with self.assertRaises(TypeError):
            self.normalize_scope(numbers)

        with self.assertRaises(TypeError):
            self.normalize_scope(True)

    def test_normalize_scope(self):

        normalized_scope_string = self.normalize_scope([])
        self.assertEqual(normalized_scope_string, "")

        normalized_scope_string_2 = self.normalize_scope(())
        self.assertEqual(normalized_scope_string_2, "")

        self.assertIsNone(self.normalize_scope(None))

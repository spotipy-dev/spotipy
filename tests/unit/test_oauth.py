# -*- coding: utf-8 -*-
import io
import json
import unittest

import six.moves.urllib.parse as urllibparse

from spotipy import SpotifyOAuth, SpotifyImplicitGrant, SpotifyPKCE
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.oauth2 import SpotifyStateError

try:
    import unittest.mock as mock
except ImportError:
    import mock

patch = mock.patch
DEFAULT = mock.DEFAULT


def _make_fake_token(expires_at, expires_in, scope):
    return dict(
        expires_at=expires_at,
        expires_in=expires_in,
        scope=scope,
        token_type="Bearer",
        refresh_token="REFRESH",
        access_token="ACCESS")


def _fake_file():
    return mock.Mock(spec_set=io.FileIO)


def _token_file(token):
    fi = _fake_file()
    fi.read.return_value = token
    return fi


def _make_oauth(*args, **kwargs):
    return SpotifyOAuth("CLID", "CLISEC", "REDIR", "STATE", *args, **kwargs)


def _make_implicitgrantauth(*args, **kwargs):
    return SpotifyImplicitGrant("CLID", "REDIR", "STATE", *args, **kwargs)


def _make_pkceauth(*args, **kwargs):
    return SpotifyPKCE("CLID", "REDIR", "STATE", *args, **kwargs)


class OAuthCacheTest(unittest.TestCase):

    @patch.multiple(SpotifyOAuth,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_gets_from_cache_path(self, opener,
                                  is_token_expired, refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_oauth(scope, path)
        cached_tok = spot.validate_token(spot.cache_handler.get_cached_token())
        cached_tok_legacy = spot.get_cached_token()

        opener.assert_called_with(path)
        self.assertIsNotNone(cached_tok)
        self.assertIsNotNone(cached_tok_legacy)
        self.assertEqual(refresh_access_token.call_count, 0)

    @patch.multiple(SpotifyOAuth,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_expired_token_refreshes(self, opener,
                                     is_token_expired, refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        expired_tok = _make_fake_token(0, None, scope)
        fresh_tok = _make_fake_token(1, 1, scope)

        token_file = _token_file(json.dumps(expired_tok, ensure_ascii=False))
        opener.return_value = token_file
        refresh_access_token.return_value = fresh_tok

        spot = _make_oauth(scope, path)
        spot.validate_token(spot.cache_handler.get_cached_token())

        is_token_expired.assert_called_with(expired_tok)
        refresh_access_token.assert_called_with(expired_tok['refresh_token'])
        opener.assert_any_call(path)

    @patch.multiple(SpotifyOAuth,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_badly_scoped_token_bails(self, opener,
                                      is_token_expired, refresh_access_token):
        token_scope = "playlist-modify-public"
        requested_scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, token_scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_oauth(requested_scope, path)
        cached_tok = spot.validate_token(spot.cache_handler.get_cached_token())

        opener.assert_called_with(path)
        self.assertIsNone(cached_tok)
        self.assertEqual(refresh_access_token.call_count, 0)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyOAuth("CLID", "CLISEC", "REDIR", "STATE", scope, path)
        spot.cache_handler.save_token_to_cache(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path_legacy(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyOAuth("CLID", "CLISEC", "REDIR", "STATE", scope, path)
        spot._save_token_info(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)

    def test_cache_handler(self):
        scope = "playlist-modify-private"
        tok = _make_fake_token(1, 1, scope)

        spot = _make_oauth(scope, cache_handler=MemoryCacheHandler())
        spot.cache_handler.save_token_to_cache(tok)
        cached_tok = spot.cache_handler.get_cached_token()

        self.assertEqual(tok, cached_tok)


class TestSpotifyOAuthGetAuthorizeUrl(unittest.TestCase):

    def test_get_authorize_url_doesnt_pass_state_by_default(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR")

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn('state', parsed_qs)

    def test_get_authorize_url_passes_state_from_constructor(self):
        state = "STATE"
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", state)

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

    def test_get_authorize_url_passes_state_from_func_call(self):
        state = "STATE"
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", "NOT STATE")

        url = oauth.get_authorize_url(state=state)

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

    def test_get_authorize_url_does_not_show_dialog_by_default(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR")

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn('show_dialog', parsed_qs)

    def test_get_authorize_url_shows_dialog_when_requested(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", show_dialog=True)

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertTrue(parsed_qs['show_dialog'])


class TestSpotifyOAuthGetAuthResponseInteractive(unittest.TestCase):

    @patch('spotipy.oauth2.webbrowser')
    @patch(
        'spotipy.oauth2.SpotifyOAuth._get_user_input',
        return_value="redir.io?code=abcde"
    )
    def test_get_auth_response_without_state(self, webbrowser_mock, get_user_input_mock):
        oauth = SpotifyOAuth("CLID", "CLISEC", "redir.io")
        code = oauth.get_auth_response()
        self.assertEqual(code, "abcde")

    @patch('spotipy.oauth2.webbrowser')
    @patch(
        'spotipy.oauth2.SpotifyOAuth._get_user_input',
        return_value="redir.io?code=abcde&state=wxyz"
    )
    def test_get_auth_response_with_consistent_state(self, webbrowser_mock, get_user_input_mock):
        oauth = SpotifyOAuth("CLID", "CLISEC", "redir.io", state='wxyz')
        code = oauth.get_auth_response()
        self.assertEqual(code, "abcde")

    @patch('spotipy.oauth2.webbrowser')
    @patch(
        'spotipy.oauth2.SpotifyOAuth._get_user_input',
        return_value="redir.io?code=abcde&state=someotherstate"
    )
    def test_get_auth_response_with_inconsistent_state(self, webbrowser_mock, get_user_input_mock):
        oauth = SpotifyOAuth("CLID", "CLISEC", "redir.io", state='wxyz')

        with self.assertRaises(SpotifyStateError):
            oauth.get_auth_response()


class TestSpotifyClientCredentials(unittest.TestCase):

    def test_spotify_client_credentials_get_access_token(self):
        oauth = SpotifyClientCredentials(client_id='ID', client_secret='SECRET')
        with self.assertRaises(SpotifyOauthError) as error:
            oauth.get_access_token(check_cache=False)
        self.assertEqual(error.exception.error, 'invalid_client')


class ImplicitGrantCacheTest(unittest.TestCase):

    @patch.object(SpotifyImplicitGrant, "is_token_expired", DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_gets_from_cache_path(self, opener, is_token_expired):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_implicitgrantauth(scope, path)
        cached_tok = spot.cache_handler.get_cached_token()
        cached_tok_legacy = spot.get_cached_token()

        opener.assert_called_with(path)
        self.assertIsNotNone(cached_tok)
        self.assertIsNotNone(cached_tok_legacy)

    @patch.object(SpotifyImplicitGrant, "is_token_expired", DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_expired_token_returns_none(self, opener, is_token_expired):
        scope = "playlist-modify-private"
        path = ".cache-username"
        expired_tok = _make_fake_token(0, None, scope)

        token_file = _token_file(json.dumps(expired_tok, ensure_ascii=False))
        opener.return_value = token_file

        spot = _make_implicitgrantauth(scope, path)
        cached_tok = spot.validate_token(spot.cache_handler.get_cached_token())

        is_token_expired.assert_called_with(expired_tok)
        opener.assert_any_call(path)
        self.assertIsNone(cached_tok)

    @patch.object(SpotifyImplicitGrant, "is_token_expired", DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_badly_scoped_token_bails(self, opener, is_token_expired):
        token_scope = "playlist-modify-public"
        requested_scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, token_scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_implicitgrantauth(requested_scope, path)
        cached_tok = spot.validate_token(spot.cache_handler.get_cached_token())

        opener.assert_called_with(path)
        self.assertIsNone(cached_tok)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyImplicitGrant("CLID", "REDIR", "STATE", scope, path)
        spot.cache_handler.save_token_to_cache(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path_legacy(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyImplicitGrant("CLID", "REDIR", "STATE", scope, path)
        spot._save_token_info(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)


class TestSpotifyImplicitGrant(unittest.TestCase):

    def test_get_authorize_url_doesnt_pass_state_by_default(self):
        auth = SpotifyImplicitGrant("CLID", "REDIR")

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn('state', parsed_qs)

    def test_get_authorize_url_passes_state_from_constructor(self):
        state = "STATE"
        auth = SpotifyImplicitGrant("CLID", "REDIR", state)

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

    def test_get_authorize_url_passes_state_from_func_call(self):
        state = "STATE"
        auth = SpotifyImplicitGrant("CLID", "REDIR", "NOT STATE")

        url = auth.get_authorize_url(state=state)

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

    def test_get_authorize_url_does_not_show_dialog_by_default(self):
        auth = SpotifyImplicitGrant("CLID", "REDIR")

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn('show_dialog', parsed_qs)

    def test_get_authorize_url_shows_dialog_when_requested(self):
        auth = SpotifyImplicitGrant("CLID", "REDIR", show_dialog=True)

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertTrue(parsed_qs['show_dialog'])


class SpotifyPKCECacheTest(unittest.TestCase):

    @patch.multiple(SpotifyPKCE,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_gets_from_cache_path(self, opener,
                                  is_token_expired, refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_pkceauth(scope, path)
        cached_tok = spot.cache_handler.get_cached_token()
        cached_tok_legacy = spot.get_cached_token()

        opener.assert_called_with(path)
        self.assertIsNotNone(cached_tok)
        self.assertIsNotNone(cached_tok_legacy)
        self.assertEqual(refresh_access_token.call_count, 0)

    @patch.multiple(SpotifyPKCE,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_expired_token_refreshes(self, opener,
                                     is_token_expired, refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        expired_tok = _make_fake_token(0, None, scope)
        fresh_tok = _make_fake_token(1, 1, scope)

        token_file = _token_file(json.dumps(expired_tok, ensure_ascii=False))
        opener.return_value = token_file
        refresh_access_token.return_value = fresh_tok

        spot = _make_pkceauth(scope, path)
        spot.validate_token(spot.cache_handler.get_cached_token())

        is_token_expired.assert_called_with(expired_tok)
        refresh_access_token.assert_called_with(expired_tok['refresh_token'])
        opener.assert_any_call(path)

    @patch.multiple(SpotifyPKCE,
                    is_token_expired=DEFAULT, refresh_access_token=DEFAULT)
    @patch('spotipy.cache_handler.open', create=True)
    def test_badly_scoped_token_bails(self, opener,
                                      is_token_expired, refresh_access_token):
        token_scope = "playlist-modify-public"
        requested_scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, token_scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        is_token_expired.return_value = False

        spot = _make_pkceauth(requested_scope, path)
        cached_tok = spot.validate_token(spot.cache_handler.get_cached_token())

        opener.assert_called_with(path)
        self.assertIsNone(cached_tok)
        self.assertEqual(refresh_access_token.call_count, 0)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyPKCE("CLID", "REDIR", "STATE", scope, path)
        spot.cache_handler.save_token_to_cache(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)

    @patch('spotipy.cache_handler.open', create=True)
    def test_saves_to_cache_path_legacy(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyPKCE("CLID", "REDIR", "STATE", scope, path)
        spot._save_token_info(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)


class TestSpotifyPKCE(unittest.TestCase):

    def test_generate_code_verifier_for_pkce(self):
        auth = SpotifyPKCE("CLID", "REDIR")
        auth.get_pkce_handshake_parameters()
        self.assertTrue(auth.code_verifier)

    def test_generate_code_challenge_for_pkce(self):
        auth = SpotifyPKCE("CLID", "REDIR")
        auth.get_pkce_handshake_parameters()
        self.assertTrue(auth.code_challenge)

    def test_code_verifier_and_code_challenge_are_correct(self):
        import hashlib
        import base64
        auth = SpotifyPKCE("CLID", "REDIR")
        auth.get_pkce_handshake_parameters()
        self.assertEqual(auth.code_challenge,
                         base64.urlsafe_b64encode(
                             hashlib.sha256(auth.code_verifier.encode('utf-8'))
                             .digest())
                         .decode('utf-8')
                         .replace('=', ''))

    def test_get_authorize_url_doesnt_pass_state_by_default(self):
        auth = SpotifyPKCE("CLID", "REDIR")

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn('state', parsed_qs)

    def test_get_authorize_url_passes_state_from_constructor(self):
        state = "STATE"
        auth = SpotifyPKCE("CLID", "REDIR", state)

        url = auth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

    def test_get_authorize_url_passes_state_from_func_call(self):
        state = "STATE"
        auth = SpotifyPKCE("CLID", "REDIR")

        url = auth.get_authorize_url(state=state)

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['state'][0], state)

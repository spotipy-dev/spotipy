from spotipy.oauth2 import SpotifyOAuth
import json
import io
import unittest

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


class OAuthCacheTest(unittest.TestCase):

    @patch.multiple(SpotifyOAuth,
                    _is_token_expired=DEFAULT, _refresh_access_token=DEFAULT)
    @patch('spotipy.oauth2.open', create=True)
    def test_gets_from_cache_path(self, opener,
                                  _is_token_expired, _refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        _is_token_expired.return_value = False

        spot = _make_oauth(scope, path)
        cached_tok = spot.get_cached_token()

        opener.assert_called_with(path)
        self.assertIsNotNone(cached_tok)
        self.assertEqual(_refresh_access_token.call_count, 0)

    @patch.multiple(SpotifyOAuth,
                    _is_token_expired=DEFAULT, _refresh_access_token=DEFAULT)
    @patch('spotipy.oauth2.open', create=True)
    def test_expired_token_refreshes(self, opener,
                                     _is_token_expired, _refresh_access_token):
        scope = "playlist-modify-private"
        path = ".cache-username"
        expired_tok = _make_fake_token(0, None, scope)
        fresh_tok = _make_fake_token(1, 1, scope)

        token_file = _token_file(json.dumps(expired_tok, ensure_ascii=False))
        opener.return_value = token_file
        _refresh_access_token.return_value = fresh_tok

        spot = _make_oauth(scope, path)
        spot.get_cached_token()

        _is_token_expired.assert_called_with(expired_tok)
        _refresh_access_token.assert_called_with(expired_tok['refresh_token'])
        opener.assert_any_call(path)

    @patch.multiple(SpotifyOAuth,
                    _is_token_expired=DEFAULT, _refresh_access_token=DEFAULT)
    @patch('spotipy.oauth2.open', create=True)
    def test_badly_scoped_token_bails(self, opener,
                                      _is_token_expired, _refresh_access_token):
        token_scope = "playlist-modify-public"
        requested_scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, token_scope)

        opener.return_value = _token_file(json.dumps(tok, ensure_ascii=False))
        _is_token_expired.return_value = False

        spot = _make_oauth(requested_scope, path)
        cached_tok = spot.get_cached_token()

        opener.assert_called_with(path)
        self.assertIsNone(cached_tok)
        self.assertEqual(_refresh_access_token.call_count, 0)

    @patch('spotipy.oauth2.open', create=True)
    def test_saves_to_cache_path(self, opener):
        scope = "playlist-modify-private"
        path = ".cache-username"
        tok = _make_fake_token(1, 1, scope)

        fi = _fake_file()
        opener.return_value = fi

        spot = SpotifyOAuth("CLID", "CLISEC", "REDIR", "STATE", scope, path)
        spot._save_token_info(tok)

        opener.assert_called_with(path, 'w')
        self.assertTrue(fi.write.called)


if __name__ == '__main__':
    unittest.main()

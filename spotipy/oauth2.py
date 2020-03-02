# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = [
    "is_token_expired",
    "SpotifyClientCredentials",
    "SpotifyOAuth",
    "SpotifyOauthError",
]

import base64
import json
import os
import sys
import time
import warnings

import requests
from spotipy.util import CLIENT_CREDS_ENV_VARS

# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse


class SpotifyOauthError(Exception):
    pass


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(
        six.text_type(client_id + ":" + client_secret).encode("ascii")
    )
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}


def is_token_expired(token_info):
    now = int(time.time())
    return token_info["expires_at"] - now < 60


def _ensure_value(value, env_key):
    env_val = CLIENT_CREDS_ENV_VARS[env_key]
    _val = value or os.getenv(env_val)
    if _val is None:
        msg = "No %s. Pass it or set a %s environment variable." % (
            env_key,
            env_val,
        )
        raise SpotifyOauthError(msg)
    return _val


class SpotifyAuthBase(object):
    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, val):
        self._client_id = _ensure_value(val, "client_id")

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val):
        self._client_secret = _ensure_value(val, "client_secret")

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val):
        self._redirect_uri = _ensure_value(val, "redirect_uri")


class SpotifyClientCredentials(SpotifyAuthBase):
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id=None, client_secret=None, proxies=None, requests_timeout=None):
        """
        You can either provide a client_id and client_secret to the
        constructor or set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
        environment variables
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_info = None
        self.proxies = proxies
        self.requests_timeout = requests_timeout

    def get_access_token(self, as_dict=True):
        """
        If a valid access token is in memory, returns it
        Else feches a new token and returns it

            Parameters:
            - as_dict - a boolean indicating if returning the access token
                as a token_info dictionary, otherwise it will be returned
                as a string.
        """
        if as_dict:
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly, or use "
                "get_cached_token instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        if self.token_info and not self.is_token_expired(self.token_info):
            return self.token_info if as_dict else self.token_info["access_token"]

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.token_info = token_info
        return self.token_info["access_token"]

    def _request_access_token(self):
        """Gets client credentials access token """
        payload = {"grant_type": "client_credentials"}

        headers = _make_authorization_headers(
            self.client_id, self.client_secret
        )

        response = requests.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        return token_info

    def is_token_expired(self, token_info):
        return is_token_expired(token_info)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        return token_info


class SpotifyOAuth(SpotifyAuthBase):
    """
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    """

    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        redirect_uri=None,
        state=None,
        scope=None,
        cache_path=None,
        username=None,
        proxies=None,
        show_dialog=False,
        requests_timeout=None
    ):
        """
            Creates a SpotifyOAuth object

            Parameters:
                 - client_id - the client id of your app
                 - client_secret - the client secret of your app
                 - redirect_uri - the redirect URI of your app
                 - state - security state
                 - scope - the desired scope of the request
                 - cache_path - path to location to save tokens
                 - requests_timeout - tell Requests to stop waiting for a response
                                      after a given number of seconds
                 - username - username of current client
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.cache_path = cache_path
        self.username = username or os.getenv(
            CLIENT_CREDS_ENV_VARS["client_username"]
        )
        self.scope = self._normalize_scope(scope)
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.show_dialog = show_dialog

    def get_cached_token(self):
        """ Gets a cached auth token
        """
        token_info = None

        if not self.cache_path and self.username:
            self.cache_path = ".cache-" + str(self.username)
        elif not self.cache_path and not self.username:
            raise SpotifyOauthError(
                "You must either set a cache_path or a username."
            )

        if self.cache_path:
            try:
                f = open(self.cache_path)
                token_info_string = f.read()
                f.close()
                token_info = json.loads(token_info_string)

                # if scopes don't match, then bail
                if "scope" not in token_info or not self._is_scope_subset(
                    self.scope, token_info["scope"]
                ):
                    return None

                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(
                        token_info["refresh_token"]
                    )

            except IOError:
                pass
        return token_info

    def _save_token_info(self, token_info):
        if self.cache_path:
            try:
                f = open(self.cache_path, "w")
                f.write(json.dumps(token_info))
                f.close()
            except IOError:
                self._warn("couldn't write token cache to " + self.cache_path)
                pass

    def _is_scope_subset(self, needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split()) if needle_scope else set()
        haystack_scope = (
            set(haystack_scope.split()) if haystack_scope else set()
        )
        return needle_scope <= haystack_scope

    def is_token_expired(self, token_info):
        return is_token_expired(token_info)

    def get_authorize_url(self, state=None):
        """ Gets the URL to use to authorize this app
        """
        payload = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if self.scope:
            payload["scope"] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload["state"] = state
        if self.show_dialog:
            payload["show_dialog"] = True

        urlparams = urllibparse.urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)

    def parse_response_code(self, url):
        """ Parse the response code in the given response url

            Parameters:
                - url - the response url
        """

        try:
            return url.split("?code=")[1].split("&")[0]
        except IndexError:
            return None

    def _make_authorization_headers(self):
        return _make_authorization_headers(self.client_id, self.client_secret)

    def get_auth_response(self):
        print(
            """

            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.

        """
        )
        auth_url = self.get_authorize_url()
        try:
            import webbrowser

            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except BaseException:
            print("Please navigate here: %s" % auth_url)
        print("")
        print("")
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")
        print("")
        print("")
        return response

    def get_authorization_code(self, response=None):
        return self.parse_response_code(response or self.get_auth_response())

    def get_access_token(self, code=None, as_dict=True, check_cache=True):
        """ Gets the access token for the app given the code

            Parameters:
                - code - the response code
                - as_dict - a boolean indicating if returning the access token
                            as a token_info dictionary, otherwise it will be returned
                            as a string.
        """
        if as_dict:
            print("")
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly, or use "
                "get_cached_token instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            print("")
        if check_cache:
            token_info = self.get_cached_token()
            if token_info is not None:
                if is_token_expired(token_info):
                    token_info = self.refresh_access_token(
                        token_info["refresh_token"]
                    )
                return token_info if as_dict else token_info["access_token"]

        payload = {
            "redirect_uri": self.redirect_uri,
            "code": code or self.get_authorization_code(),
            "grant_type": "authorization_code",
        }
        if self.scope:
            payload["scope"] = self.scope
        if self.state:
            payload["state"] = self.state

        headers = self._make_authorization_headers()

        response = requests.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self._save_token_info(token_info)
        return token_info if as_dict else token_info["access_token"]

    def _normalize_scope(self, scope):
        if scope:
            scopes = sorted(scope.split())
            return " ".join(scopes)
        else:
            return None

    def refresh_access_token(self, refresh_token):
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = self._make_authorization_headers()

        response = requests.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            if False:  # debugging code
                print("headers", headers)
                print("request", response.url)
            self._warn(
                "couldn't refresh token: code:%d reason:%s"
                % (response.status_code, response.reason)
            )
            return None
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token
        self._save_token_info(token_info)
        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        token_info["scope"] = self.scope
        return token_info

    def _warn(self, msg):
        print("warning:" + msg, file=sys.stderr)

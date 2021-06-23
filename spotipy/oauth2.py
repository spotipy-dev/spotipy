# -*- coding: utf-8 -*-

__all__ = [
    "SpotifyClientCredentials",
    "SpotifyOAuth",
    "SpotifyOauthError",
    "SpotifyStateError",
    "SpotifyPKCE"
]

import base64
import logging
import os
import re
import time
import webbrowser
from typing import Dict, Iterable, Optional, Tuple, Type, Union

import requests
# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from six.moves.urllib_parse import parse_qsl, urlparse

from spotipy.cache_handler import CacheFileHandler, CacheHandler
from spotipy.json_types import TokenInfo
from spotipy.scope import Scope
from spotipy.util import CLIENT_CREDS_ENV_VARS, get_host_port

logger = logging.getLogger(__name__)


class SpotifyOauthError(Exception):
    """ Error during Auth Code or Implicit Grant flow """

    def __init__(self, message: str, error: Optional[str] = None, error_description: Optional[str] = None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super(SpotifyOauthError, self).__init__(message, *args, **kwargs)


class SpotifyStateError(SpotifyOauthError):
    """ The state sent and state recieved were different """

    def __init__(self, local_state: Optional[str] = None, remote_state: Optional[str] = None, message: Optional[str] = None,
                 error: Optional[str] = None, error_description: Optional[str] = None, *args, **kwargs):
        if not message:
            message = ("Expected " + local_state + " but recieved "
                       + remote_state)
        super(SpotifyOauthError, self).__init__(message, error,
                                                error_description, *args,
                                                **kwargs)


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(
        six.text_type(client_id + ":" + client_secret).encode("ascii")
    )
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}


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

    def __init__(self, requests_session: requests.Session):
        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                from requests import api
                self._session = api

    def _normalize_scope(self, scope):
        """
        Accepts a string of scopes, or an iterable with elements of type
        `Scope` or `str` and returns a space-separated string of scopes.
        Returns `None` if the argument is `None`.
        """

        # TODO: do we need to sort the scopes?

        if isinstance(scope, str):
            # allow for any separator(s) between the scopes other than a word
            # character or a hyphen
            scopes = re.split(pattern=r"[^\w-]+", string=scope)
            return " ".join(sorted(scopes))

        if isinstance(scope, Iterable):

            # Assume all of the iterable's elements are of the same type.
            # If the iterable is empty, then return None.
            first_element = next(iter(scope), None)

            if isinstance(first_element, str):
                return " ".join(sorted(scope))
            if isinstance(first_element, Scope):
                return Scope.make_string(scope)
            if first_element is None:
                return ""

        elif scope is None:
            return None

        raise TypeError(
            "Unsupported type for scopes: %s. Expected either a string of scopes, or "
            "an Iterable with elements of type `Scope` or `str`." % type(scope)
        )

    @property
    def client_id(self) -> str:
        return self._client_id

    @client_id.setter
    def client_id(self, val: str):
        self._client_id = _ensure_value(val, "client_id")

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val: str):
        self._client_secret = _ensure_value(val, "client_secret")

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val: str):
        self._redirect_uri = _ensure_value(val, "redirect_uri")

    @staticmethod
    def _get_user_input(prompt):
        try:
            return raw_input(prompt)
        except NameError:
            return input(prompt)

    @staticmethod
    def is_token_expired(token_info: TokenInfo) -> bool:
        now = int(time.time())
        return token_info["expires_at"] - now < 60

    @staticmethod
    def _is_scope_subset(needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split()) if needle_scope else set()
        haystack_scope = (
            set(haystack_scope.split()) if haystack_scope else set()
        )
        return needle_scope <= haystack_scope

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if isinstance(self._session, requests.Session):
            self._session.close()


class SpotifyClientCredentials(SpotifyAuthBase):
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        cache_handler: CacheHandler = None,
        proxies: Optional[Dict[str, str]] = None,
        requests_session: Union[requests.Session, bool] = True,
        requests_timeout: Optional[int] = None
    ):
        """
        Creates a Client Credentials Flow Manager.

        The Client Credentials flow is used in server-to-server authentication.
        Only endpoints that do not access user information can be accessed.
        This means that endpoints that require authorization scopes cannot be accessed.
        The advantage, however, of this authorization flow is that it does not require any
        user interaction

        You can either provide a client_id and client_secret to the
        constructor or set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
        environment variables

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * cache_handler: An instance of the `CacheHandler` class to handle
                              getting and saving cached authorization tokens.
                              Optional, will otherwise use `CacheFileHandler`.
             * proxies: Optional, proxy for the requests library to route through
             * requests_session: A Requests session object or a true value to create one.
                                 A false value disables sessions.
                                 It should generally be a good idea to keep sessions enabled
                                 for performance reasons (connection pooling).
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds

        """

        super(SpotifyClientCredentials, self).__init__(requests_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        if cache_handler:
            assert issubclass(cache_handler.__class__, CacheHandler), \
                "cache_handler must be a subclass of CacheHandler: " + str(type(cache_handler)) \
                + " != " + str(CacheHandler)
            self.cache_handler = cache_handler
        else:
            self.cache_handler = CacheFileHandler()

    def get_access_token(self, check_cache: bool = True) -> str:
        """
        If a valid access token is in memory, returns it
        Else feches a new token and returns it

            Parameters:
            - check_cache - if true, checks for a locally stored token
                            before requesting a new token.
        """

        if check_cache:
            token_info = self.cache_handler.get_cached_token()
            if token_info and not self.is_token_expired(token_info):
                return token_info["access_token"]

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.cache_handler.save_token_to_cache(token_info)
        return token_info["access_token"]

    def _request_access_token(self):
        """Gets client credentials access token """
        payload = {"grant_type": "client_credentials"}

        headers = _make_authorization_headers(
            self.client_id, self.client_secret
        )

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            error_payload = response.json()
            raise SpotifyOauthError(
                'error: {0}, error_description: {1}'.format(
                    error_payload['error'], error_payload['error_description']),
                error=error_payload['error'],
                error_description=error_payload['error_description'])
        token_info = response.json()
        return token_info

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
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            redirect_uri: Optional[str] = None,
            state: Optional[str] = None,
            scope: Optional[Union[str, Iterable[Union[Scope, str]]]] = None,
            cache_handler: Optional[CacheHandler] = None,
            proxies: Optional[Dict[str, str]] = None,
            show_dialog: bool = False,
            requests_session: Union[requests.Session, bool] = True,
            requests_timeout: Optional[int] = None,
            open_browser: bool = True
    ):
        """
        Creates a SpotifyOAuth object

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * redirect_uri: Must be supplied or set as environment variable
             * state: Optional, no verification is performed
             * scope: Optional, either a string of scopes, or an iterable with elements of type
                      `Scope` or `str`. E.g.,
                      {Scope.user_modify_playback_state, Scope.user_library_read}
             * cache_handler: An instance of the `CacheHandler` class to handle
                              getting and saving cached authorization tokens.
                              Optional, will otherwise use `CacheFileHandler`.
             * proxies: Optional, proxy for the requests library to route through
             * show_dialog: Optional, interpreted as boolean
             * requests_session: A Requests session object or a true value to create one.
                                 A false value disables sessions.
                                 It should generally be a good idea to keep sessions enabled
                                 for performance reasons (connection pooling).
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
             * open_browser: Optional, whether or not the web browser should be opened to
                             authorize a user
        """

        super(SpotifyOAuth, self).__init__(requests_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = self._normalize_scope(scope)
        if cache_handler:
            assert issubclass(cache_handler.__class__, CacheHandler), \
                "cache_handler must be a subclass of CacheHandler: " + str(type(cache_handler)) \
                + " != " + str(CacheHandler)
            self.cache_handler = cache_handler
        else:
            self.cache_handler = CacheFileHandler()
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.show_dialog = show_dialog
        self.open_browser = open_browser

    def validate_token(self, token_info: Optional[TokenInfo]) -> Optional[TokenInfo]:
        if token_info is None:
            return None

        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
                self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(
                token_info["refresh_token"]
            )

        return token_info

    def get_authorize_url(self, state: Optional[str] = None) -> str:
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

    def parse_response_code(self, url: str) -> str:
        """ Parse the response code in the given response url

            Parameters:
                - url - the response url
        """
        _, code = self.parse_auth_response_url(url)
        if code is None:
            return url
        else:
            return code

    @staticmethod
    def parse_auth_response_url(url: str) -> Tuple[Optional[str], ...]:
        query_s = urlparse(url).query
        form = dict(parse_qsl(query_s))
        if "error" in form:
            raise SpotifyOauthError("Received error from auth server: "
                                    "{}".format(form["error"]),
                                    error=form["error"])
        return tuple(form.get(param) for param in ["state", "code"])

    def _make_authorization_headers(self):
        return _make_authorization_headers(self.client_id, self.client_secret)

    def _open_auth_url(self):
        auth_url = self.get_authorize_url()
        try:
            webbrowser.open(auth_url)
            logger.info("Opened %s in your browser", auth_url)
        except webbrowser.Error:
            logger.error("Please navigate here: %s", auth_url)

    def _get_auth_response_interactive(self, open_browser=False):
        if open_browser:
            self._open_auth_url()
            prompt = "Enter the URL you were redirected to: "
        else:
            url = self.get_authorize_url()
            prompt = (
                "Go to the following URL: {}\n"
                "Enter the URL you were redirected to: ".format(url)
            )
        response = self._get_user_input(prompt)
        state, code = SpotifyOAuth.parse_auth_response_url(response)
        if self.state is not None and self.state != state:
            raise SpotifyStateError(self.state, state)
        return code

    def _get_auth_response_local_server(self, redirect_port):
        server = start_local_http_server(redirect_port)
        self._open_auth_url()
        server.handle_request()

        if self.state is not None and server.state != self.state:
            raise SpotifyStateError(self.state, server.state)

        if server.auth_code is not None:
            return server.auth_code
        elif server.error is not None:
            raise server.error
        else:
            raise SpotifyOauthError("Server listening on localhost has not been accessed")

    def get_auth_response(self, open_browser: Optional[bool] = None) -> str:
        logger.info('User authentication requires interaction with your '
                    'web browser. Once you enter your credentials and '
                    'give authorization, you will be redirected to '
                    'a url.  Paste that url you were directed to to '
                    'complete the authorization.')

        redirect_info = urlparse(self.redirect_uri)
        redirect_host, redirect_port = get_host_port(redirect_info.netloc)

        if open_browser is None:
            open_browser = self.open_browser

        if (
                open_browser
                and redirect_host in ("127.0.0.1", "localhost")
                and redirect_info.scheme == "http"
        ):
            # Only start a local http server if a port is specified
            if redirect_port:
                return self._get_auth_response_local_server(redirect_port)
            else:
                logger.warning('Using `%s` as redirect URI without a port. '
                               'Specify a port (e.g. `%s:8080`) to allow '
                               'automatic retrieval of authentication code '
                               'instead of having to copy and paste '
                               'the URL your browser is redirected to.',
                               redirect_host, redirect_host)

        return self._get_auth_response_interactive(open_browser=open_browser)

    def get_authorization_code(self, response: Optional[str] = None) -> str:
        if response:
            return self.parse_response_code(response)
        return self.get_auth_response()

    def get_access_token(self, code: Optional[str] = None, check_cache: bool = True) -> str:
        """ Gets the access token for the app given the code

            Parameters:
                - code - the response code
                - check_cache - if true, checks for a locally stored token
                                before requesting a new token
        """
        if check_cache:
            token_info = self.validate_token(self.cache_handler.get_cached_token())
            if token_info is not None:
                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(
                        token_info["refresh_token"]
                    )
                return token_info["access_token"]

        payload = {
            "redirect_uri": self.redirect_uri,
            "code": code or self.get_auth_response(),
            "grant_type": "authorization_code",
        }
        if self.scope:
            payload["scope"] = self.scope
        if self.state:
            payload["state"] = self.state

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            error_payload = response.json()
            raise SpotifyOauthError(
                'error: {0}, error_description: {1}'.format(
                    error_payload['error'], error_payload['error_description']),
                error=error_payload['error'],
                error_description=error_payload['error_description'])
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.cache_handler.save_token_to_cache(token_info)
        return token_info["access_token"]

    def refresh_access_token(self, refresh_token: str) -> TokenInfo:
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )

        if response.status_code != 200:
            error_payload = response.json()
            raise SpotifyOauthError(
                'error: {0}, error_description: {1}'.format(
                    error_payload['error'], error_payload['error_description']),
                error=error_payload['error'],
                error_description=error_payload['error_description'])

        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token
        self.cache_handler.save_token_to_cache(token_info)
        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        token_info["scope"] = self.scope
        return token_info


class SpotifyPKCE(SpotifyAuthBase):
    """ Implements PKCE Authorization Flow for client apps

    This auth manager enables *user and non-user* endpoints with only
    a client secret, redirect uri, and username. When the app requests
    an an access token for the first time, the user is prompted to
    authorize the new client app. After authorizing the app, the client
    app is then given both access and refresh tokens. This is the
    preferred way of authorizing a mobile/desktop client.

    """

    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        scope: Optional[Union[str, Iterable[Union[Scope, str]]]] = None,
        cache_handler: Optional[CacheHandler] = None,
        proxies: Optional[Dict[str, str]] = None,
        requests_timeout: Optional[int] = None,
        requests_session: Union[requests.Session, bool] = True,
        open_browser: bool = True
    ):
        """
        Creates Auth Manager with the PKCE Auth flow.

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * redirect_uri: Must be supplied or set as environment variable
             * state: Optional, no verification is performed
             * scope: Optional, either a string of scopes, or an iterable with elements of type
                      `Scope` or `str`. E.g.,
                      {Scope.user_modify_playback_state, Scope.user_library_read}
             * cache_handler: An instance of the `CacheHandler` class to handle
                              getting and saving cached authorization tokens.
                              Optional, will otherwise use `CacheFileHandler`.
             * proxies: Optional, proxy for the requests library to route through
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
             * requests_session: A Requests session object or a true value to create one.
                                 A false value disables sessions.
                                 It should generally be a good idea to keep sessions enabled
                                 for performance reasons (connection pooling).
             * open_browser: Optional, thether or not the web browser should be opened to
                             authorize a user
        """

        super(SpotifyPKCE, self).__init__(requests_session)
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = self._normalize_scope(scope)
        if cache_handler:
            assert issubclass(cache_handler.__class__, CacheHandler), \
                "cache_handler must be a subclass of CacheHandler: " + str(type(cache_handler)) \
                + " != " + str(CacheHandler)
            self.cache_handler = cache_handler
        else:
            self.cache_handler = CacheFileHandler()
        self.proxies = proxies
        self.requests_timeout = requests_timeout

        self._code_challenge_method = "S256"  # Spotify requires SHA256
        self.code_verifier = None
        self.code_challenge = None
        self.authorization_code = None
        self.open_browser = open_browser

    def _get_code_verifier(self):
        """ Spotify PCKE code verifier - See step 1 of the reference guide below
        Reference:
        https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow-with-proof-key-for-code-exchange-pkce
        """
        # Range (33,96) is used to select between 44-128 base64 characters for the
        # next operation. The range looks weird because base64 is 6 bytes
        import random
        length = random.randint(33, 96)

        # The seeded length generates between a 44 and 128 base64 characters encoded string
        try:
            import secrets
            verifier = secrets.token_urlsafe(length)
        except ImportError:  # For python 3.5 support
            import base64
            import os
            rand_bytes = os.urandom(length)
            verifier = base64.urlsafe_b64encode(rand_bytes).decode('utf-8').replace('=', '')
        return verifier

    def _get_code_challenge(self):
        """ Spotify PCKE code challenge - See step 1 of the reference guide below
        Reference:
        https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow-with-proof-key-for-code-exchange-pkce
        """
        import base64
        import hashlib
        code_challenge_digest = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode('utf-8')
        return code_challenge.replace('=', '')

    def get_authorize_url(self, state: Optional[str] = None) -> str:
        """ Gets the URL to use to authorize this app """
        if not self.code_challenge:
            self.get_pkce_handshake_parameters()
        payload = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "code_challenge_method": self._code_challenge_method,
            "code_challenge": self.code_challenge
        }
        if self.scope:
            payload["scope"] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload["state"] = state
        urlparams = urllibparse.urlencode(payload)
        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)

    def _open_auth_url(self, state=None):
        auth_url = self.get_authorize_url(state)
        try:
            webbrowser.open(auth_url)
            logger.info("Opened %s in your browser", auth_url)
        except webbrowser.Error:
            logger.error("Please navigate here: %s", auth_url)

    def _get_auth_response(self, open_browser=None):
        logger.info('User authentication requires interaction with your '
                    'web browser. Once you enter your credentials and '
                    'give authorization, you will be redirected to '
                    'a url.  Paste that url you were directed to to '
                    'complete the authorization.')

        redirect_info = urlparse(self.redirect_uri)
        redirect_host, redirect_port = get_host_port(redirect_info.netloc)

        if open_browser is None:
            open_browser = self.open_browser

        if (
                open_browser
                and redirect_host in ("127.0.0.1", "localhost")
                and redirect_info.scheme == "http"
        ):
            # Only start a local http server if a port is specified
            if redirect_port:
                return self._get_auth_response_local_server(redirect_port)
            else:
                logger.warning('Using `%s` as redirect URI without a port. '
                               'Specify a port (e.g. `%s:8080`) to allow '
                               'automatic retrieval of authentication code '
                               'instead of having to copy and paste '
                               'the URL your browser is redirected to.',
                               redirect_host, redirect_host)
        return self._get_auth_response_interactive(open_browser=open_browser)

    def _get_auth_response_local_server(self, redirect_port):
        server = start_local_http_server(redirect_port)
        self._open_auth_url()
        server.handle_request()

        if self.state is not None and server.state != self.state:
            raise SpotifyStateError(self.state, server.state)

        if server.auth_code is not None:
            return server.auth_code
        elif server.error is not None:
            raise SpotifyOauthError("Received error from OAuth server: {}".format(server.error))
        else:
            raise SpotifyOauthError("Server listening on localhost has not been accessed")

    def _get_auth_response_interactive(self, open_browser=False):
        if open_browser or self.open_browser:
            self._open_auth_url()
            prompt = "Enter the URL you were redirected to: "
        else:
            url = self.get_authorize_url()
            prompt = (
                "Go to the following URL: {}\n"
                "Enter the URL you were redirected to: ".format(url)
            )
        response = self._get_user_input(prompt)
        state, code = self.parse_auth_response_url(response)
        if self.state is not None and self.state != state:
            raise SpotifyStateError(self.state, state)
        return code

    def get_authorization_code(self, response: str = None) -> str:
        if response:
            return self.parse_response_code(response)
        return self._get_auth_response()

    def validate_token(self, token_info: TokenInfo) -> Optional[TokenInfo]:
        if token_info is None:
            return None

        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
                self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(
                token_info["refresh_token"]
            )

        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        return token_info

    def get_pkce_handshake_parameters(self) -> None:
        self.code_verifier = self._get_code_verifier()
        self.code_challenge = self._get_code_challenge()

    def get_access_token(self, code: Optional[str] = None, check_cache: bool = True):
        """ Gets the access token for the app

            If the code is not given and no cached token is used, an
            authentication window will be shown to the user to get a new
            code.

            Parameters:
                - code - the response code from authentication
                - check_cache - if true, checks for a locally stored token
                                before requesting a new token
        """

        if check_cache:
            token_info = self.validate_token(self.cache_handler.get_cached_token())
            if token_info is not None:
                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(
                        token_info["refresh_token"]
                    )
                return token_info["access_token"]

        if self.code_verifier is None or self.code_challenge is None:
            self.get_pkce_handshake_parameters()

        payload = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "code": code or self.get_authorization_code(),
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            verify=True,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )
        if response.status_code != 200:
            error_payload = response.json()
            raise SpotifyOauthError('error: {0}, error_descr: {1}'.format(error_payload['error'],
                                                                          error_payload[
                                                                              'error_description'
            ]),
                error=error_payload['error'],
                error_description=error_payload['error_description'])
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.cache_handler.save_token_to_cache(token_info)
        return token_info["access_token"]

    def refresh_access_token(self, refresh_token: str) -> TokenInfo:
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.client_id,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL, headers, payload
        )

        response = self._session.post(
            self.OAUTH_TOKEN_URL,
            data=payload,
            headers=headers,
            proxies=self.proxies,
            timeout=self.requests_timeout,
        )

        if response.status_code != 200:
            error_payload = response.json()
            raise SpotifyOauthError(
                'error: {0}, error_description: {1}'.format(
                    error_payload['error'], error_payload['error_description']),
                error=error_payload['error'],
                error_description=error_payload['error_description'])

        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if "refresh_token" not in token_info:
            token_info["refresh_token"] = refresh_token
        self.cache_handler.save_token_to_cache(token_info)
        return token_info

    def parse_response_code(self, url: str) -> str:
        """ Parse the response code in the given response url

            Parameters:
                - url - the response url
        """
        _, code = self.parse_auth_response_url(url)
        if code is None:
            return url
        else:
            return code

    @staticmethod
    def parse_auth_response_url(url: str) -> Tuple[Optional[str], ...]:
        return SpotifyOAuth.parse_auth_response_url(url)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.auth_code = self.server.error = None
        try:
            state, auth_code = SpotifyOAuth.parse_auth_response_url(self.path)
            self.server.state = state
            self.server.auth_code = auth_code
        except SpotifyOauthError as error:
            self.server.error = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if self.server.auth_code:
            status = "successful"
        elif self.server.error:
            status = "failed ({})".format(self.server.error)
        else:
            self._write("<html><body><h1>Invalid request</h1></body></html>")
            return

        self._write("""<html>
<script>
window.close()
</script>
<body>
<h1>Authentication status: {}</h1>
This window can be closed.
<script>
window.close()
</script>
<button class="closeButton" style="cursor: pointer" onclick="window.close();">Close Window</button>
</body>
</html>""".format(status))

    def _write(self, text):
        return self.wfile.write(text.encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_local_http_server(port: int, handler: Type[BaseHTTPRequestHandler] = RequestHandler) -> HTTPServer:
    server = HTTPServer(("127.0.0.1", port), handler)
    server.allow_reuse_address = True
    server.auth_code = None
    server.auth_token_form = None
    server.error = None
    return server

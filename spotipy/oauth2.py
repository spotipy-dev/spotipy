
from __future__ import print_function
import base64
import requests
import os
import json
import time
import sys

# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse


class SpotifyOauthError(Exception):
    pass


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
    return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}


def is_token_expired(token_info):
    now = int(time.time())
    return token_info['expires_at'] - now < 60


class SpotifyClientCredentials(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id=None, client_secret=None, proxies=None):
        """
        You can either provid a client_id and client_secret to the
        constructor or set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
        environment variables
        """
        if not client_id:
            client_id = os.getenv('SPOTIPY_CLIENT_ID')

        if not client_secret:
            client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

        if not client_id:
            raise SpotifyOauthError('No client id')

        if not client_secret:
            raise SpotifyOauthError('No client secret')

        self.client_id = client_id
        self.client_secret = client_secret
        self.token_info = None
        self.proxies = proxies

    def get_access_token(self):
        """
        If a valid access token is in memory, returns it
        Else feches a new token and returns it
        """
        if self.token_info and not self.is_token_expired(self.token_info):
            return self.token_info['access_token']

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.token_info = token_info
        return self.token_info['access_token']

    def _request_access_token(self):
        """Gets client credentials access token """
        payload = { 'grant_type': 'client_credentials'}

        headers = _make_authorization_headers(self.client_id, self.client_secret)

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, verify=True, proxies=self.proxies)
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
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        return token_info


class SpotifyOAuth(object):
    '''
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    '''

    OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, redirect_uri,
            state=None, scope=None, cache_path=None, proxies=None):
        '''
            Creates a SpotifyOAuth object

            Parameters:
                 - client_id - the client id of your app
                 - client_secret - the client secret of your app
                 - redirect_uri - the redirect URI of your app
                 - state - security state
                 - scope - the desired scope of the request
                 - cache_path - path to location to save tokens
        '''

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state=state
        self.cache_path = cache_path
        self.scope=self._normalize_scope(scope)
        self.proxies = proxies

    def get_cached_token(self):
        ''' Gets a cached auth token
        '''
        token_info = None
        if self.cache_path:
            try:
                f = open(self.cache_path)
                token_info_string = f.read()
                f.close()
                token_info = json.loads(token_info_string)

                # if scopes don't match, then bail
                if 'scope' not in token_info or not self._is_scope_subset(self.scope, token_info['scope']):
                    return None

                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(token_info['refresh_token'])

            except IOError:
                pass
        return token_info

    def _save_token_info(self, token_info):
        if self.cache_path:
            try:
                f = open(self.cache_path, 'w')
                f.write(json.dumps(token_info))
                f.close()
            except IOError:
                self._warn("couldn't write token cache to " + self.cache_path)
                pass

    def _is_scope_subset(self, needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split()) if needle_scope else set()
        haystack_scope = set(haystack_scope.split()) if haystack_scope else set()
        return needle_scope <= haystack_scope

    def is_token_expired(self, token_info):
        return is_token_expired(token_info)

    def get_authorize_url(self, state=None, show_dialog=False):
        """ Gets the URL to use to authorize this app
        """
        payload = {'client_id': self.client_id,
                   'response_type': 'code',
                   'redirect_uri': self.redirect_uri}
        if self.scope:
            payload['scope'] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload['state'] = state
        if show_dialog:
            payload['show_dialog'] = True

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

    def get_access_token(self, code):
        """ Gets the access token for the app given the code

            Parameters:
                - code - the response code
        """

        payload = {'redirect_uri': self.redirect_uri,
                   'code': code,
                   'grant_type': 'authorization_code'}
        if self.scope:
            payload['scope'] = self.scope
        if self.state:
            payload['state'] = self.state

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, verify=True, proxies=self.proxies)
        if response.status_code != 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self._save_token_info(token_info)
        return token_info

    def _normalize_scope(self, scope):
        if scope:
            scopes = scope.split()
            scopes.sort()
            return ' '.join(scopes)
        else:
            return None

    def refresh_access_token(self, refresh_token):
        payload = { 'refresh_token': refresh_token,
                   'grant_type': 'refresh_token'}

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, proxies=self.proxies)
        if response.status_code != 200:
            if False:  # debugging code
                print('headers', headers)
                print('request', response.url)
            self._warn("couldn't refresh token: code:%d reason:%s" \
                % (response.status_code, response.reason))
            return None
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if not 'refresh_token' in token_info:
            token_info['refresh_token'] = refresh_token
        self._save_token_info(token_info)
        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        '''
        Store some values that aren't directly provided by a Web API
        response.
        '''
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        token_info['scope'] = self.scope
        return token_info

    def _warn(self, msg):
        print('warning:' + msg, file=sys.stderr)


import base64
import urllib
import requests
import os
import json
import time

class SpotifyOauthError(Exception):
    pass

class SpotifyOAuth(object):
    '''
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    Docs: https://developer.spotify.com/spotify-web-api/authorization-guide/#authorization_code_flow
    '''

    OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, redirect_uri, 
            state=None, scope=None, cache_path=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state=state
        self.cache_path = cache_path
        self.scope=self.normalize_scope(scope)
   
    def get_cached_token(self):
        token_info = None
        if self.cache_path:
            try:
                f = open(self.cache_path)
                token_info_string = f.read()
                f.close()
                token_info = json.loads(token_info_string)

                # if scopes don't match, then bail
                if 'scope' not in token_info or self.scope != token_info['scope']:
                    return None

                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(token_info['refresh_token'])

            except IOError:
                pass
        return token_info

    def save_token_info(self, token_info):
        if self.cache_path:
            f = open(self.cache_path, 'w')
            print >>f, json.dumps(token_info)
            f.close()

    def is_token_expired(self, token_info):
        now = int(time.time())
        return token_info['expires_at'] < now
        
    def get_authorize_url(self):
        payload = {'client_id': self.client_id,
                   'response_type': 'code',
                   'redirect_uri': self.redirect_uri}
        if self.scope:
            payload['scope'] = self.scope
        if self.state:
            payload['state'] = self.state

        urlparams = urllib.urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)

    def parse_response_code(self, response):
        try:
            return response.split("?code=")[1].split("&")[0]
        except IndexError:
            return None

    def get_access_token(self, code):
        payload = {'redirect_uri': self.redirect_uri,
                   'code': code,
                   'grant_type': 'authorization_code'}
        if self.scope:
            payload['scope'] = self.scope
        if self.state:
            payload['state'] = self.state

        auth_header = base64.b64encode(self.client_id + ':' + self.client_secret)
        headers = {'Authorization': 'Basic %s' % auth_header}


        response = requests.post(self.OAUTH_TOKEN_URL, data=payload, 
            headers=headers, verify=True)
        if response.status_code is not 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.save_token_info(token_info)
        return token_info

    def normalize_scope(self, scope):
        if scope:
            scopes = scope.split()
            scopes.sort()
            return ' '.join(scopes)
        else:
            return None

    def refresh_access_token(self, refresh_token):
        payload = { 'refresh_token': refresh_token,
                   'grant_type': 'refresh_token'}

        auth_header = base64.b64encode(self.client_id + ':' + self.client_secret)
        headers = {'Authorization': 'Basic %s' % auth_header}
        response = requests.post(self.OAUTH_TOKEN_URL, data=payload, 
            headers=headers, verify=True)
        if response.status_code is not 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if not 'refresh_token' in token_info:
            token_info['refresh_token'] = refresh_token
        self.save_token_info(token_info)
        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        ''' 
        Store some values that aren't directly provided by a Web API
        response.
        '''
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        token_info['scope'] = self.scope
        return token_info


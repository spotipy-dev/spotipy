import base64
import urllib
import requests


class SpotifyOauthError(Exception):
    pass

class SpotifyOAuth(object):
    '''
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    Docs: https://developer.spotify.com/spotify-web-api/authorization-guide/#authorization_code_flow
    '''

    OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
    def __init__(self, client_id, client_secret, redirect_uri, state=None, scope=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state=state
        self.scope=scope

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
        return response.split("?code=")[1].split("&")[0]

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


        response = requests.post(self.OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)
        if response.status_code is not 200:
            raise SpotifyOauthError(response.reason)
        return response.json()['access_token']
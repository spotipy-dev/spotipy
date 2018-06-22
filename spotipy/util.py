from __future__ import print_function
import os
from threading import RLock, Thread, Event
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from . import oauth2
import spotipy


class AuthLocalWebserver(object):

    def __init__(self, redirect_uri):
        self.redirect_uri = redirect_uri
        url = urlparse(redirect_uri)
        self.scheme = url.scheme
        self.hostname = url.hostname
        self.port = url.port
        self.httpd = None
        self.url_lock = RLock()
        self.oauth_url = None

    def _make_handler_class(self):
        ws = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                # TODO there must be a better way
                ws.oauth_url = ws.scheme + ws.hostname + ':' + str(ws.port) + \
                    self.path
                self.send_response(200)
                self.end_headers()
                self.wfile.write('You can now close this page.'.encode('utf-8'))
                self.wfile.close()
        return Handler

    def start(self):
        self.httpd = HTTPServer((self.hostname, self.port),
                                self._make_handler_class())
        ev = Event()
        thread = Thread(target=self.serve, daemon=True, args=(ev,))
        thread.start()
        return ev

    def serve(self, event):
        self.url_lock.acquire()
        event.set()
        # handle only one request
        self.httpd.handle_request()
        self.url_lock.release()

    def get_oauth_url(self):
        # make sure we block until we get the url from spotify
        self.url_lock.acquire()
        url = self.oauth_url
        self.url_lock.release()
        return url


def prompt_for_user_token(username, scope=None, client_id = None,
        client_secret = None, redirect_uri = None, cache_path = None,
        local_webserver = False):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens

    '''

    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    if not client_id:
        print('''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:

            export SPOTIPY_CLIENT_ID='your-spotify-client-id'
            export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
            export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

            Get your credentials at
                https://developer.spotify.com/my-applications
        ''')
        raise spotipy.SpotifyException(550, -1, 'no credentials set')

    cache_path = cache_path or ".cache-" + username
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri,
        scope=scope, cache_path=cache_path)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        if not local_webserver:
            print('''

                User authentication requires interaction with your
                web browser. Once you enter your credentials and
                give authorization, you will be redirected to
                a url.  Paste that url you were directed to to
                complete the authorization.

            ''')
        else:
            server = AuthLocalWebserver(redirect_uri)
            ready = server.start()
            # this will ensure we block until the server starts, then
            # get_oauth_url will block until we get a request from spotify
            ready.wait()

        auth_url = sp_oauth.get_authorize_url()
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        if not local_webserver:
            print()
            print()
            try:
                response = raw_input("Enter the URL you were redirected to: ")
            except NameError:
                response = input("Enter the URL you were redirected to: ")

            print()
            print()
        else:
            response = server.get_oauth_url()

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None

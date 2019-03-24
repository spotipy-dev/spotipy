
# shows a user's playlists (need to be authenticated via oauth)

from __future__ import print_function
import os
from . import oauth2
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import spotipy

PORT = 8080
REDIRECT_ADDRESS = "http://localhost"
REDIRECT_URI = "{}:{}".format(REDIRECT_ADDRESS, PORT)


def prompt_for_user_token(username, scope=None, client_id = None,
        client_secret = None, cache_path = None):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify 
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - cache_path - path to location to save tokens

    '''

    assert_port_available(80)

    if not client_id:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

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
    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, REDIRECT_URI,
        scope=scope, cache_path=cache_path)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print('''

            User authentication requires interaction with your
            web browser. You will be prompted to enter your 
            credentials and give authorization.

        ''')
        auth_url = sp_oauth.get_authorize_url()
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        code = get_authentication_code()
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None


def assert_port_available(port):
    """
    Assert a given network port is available.
    raise SpotifyException if the port is not available
    :param port: network port to check
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", port))
    except socket.error:
        raise spotipy.SpotifyException(200, -1, "Port {} is not available. If you are currently running a server, "
                                                "please halt it for a min.".format(port))
    finally:
        s.close()


def get_authentication_code():
    """
    Create a temporary http server and get authentication code.
    As soon as a request is received, the server is closed.
    :return: the authentication code
    """
    httpd = MicroServer((REDIRECT_URI.split("://")[1].split(":")[0], PORT), CustomHandler)
    # stop the server once a request is received
    while not httpd.latest_query_components:
        httpd.handle_request()
    httpd.server_close()
    if "error" in httpd.latest_query_components:
        if httpd.latest_query_components["error"][0] == "access_denied":
            raise spotipy.SpotifyException(200, -1, 'The user rejected Spotify access')
        else:
            raise spotipy.SpotifyException(200, -1, 'Unknown error from Spotify authentication server: {}'.format(
                httpd.latest_query_components["error"][0]))
    if "code" in httpd.latest_query_components:
        code = httpd.latest_query_components["code"][0]
    else:
        raise spotipy.SpotifyException(200, -1, 'Unknown response from Spotify authentication server: {}'.format(
            httpd.latest_query_components))
    return code


class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.server.latest_query_components = parse_qs(urlparse(self.path).query)
        self.wfile.write(b"<html><body><p>You can close this tab</p></body></html>")


class MicroServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.latest_query_components = None
        super().__init__(server_address, RequestHandlerClass)


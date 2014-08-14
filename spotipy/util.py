
# shows a user's playlists (need to be authenticated via oauth)

import os
import subprocess
import sys
import oauth2

def prompt_for_user_token(username, scope=None):
    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify 
        constructor
    '''

    client_id = os.getenv('CLIENT_ID', 'YOUR_CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
    redirect_uri = os.getenv('REDIRECT_URI', 'YOUR_REDIRECT_URI')


    if client_id == 'YOUR_CLIENT_ID':
        print '''
            You need to set your Spotify API credentials. You can do this by
            setting environment variables like so:

            export CLIENT_ID='your-spotify-client-id'
            export CLIENT_SECRET='your-spotify-client-secret'
            export REDIRECT_URI='your-app-redirect-url'

            Get your credentials at https://developer.spotify.com/my-applications
        '''
        sys.exit(1)

    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, 
        scope=scope, cache_path=username)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        try:
            subprocess.call(["open", auth_url])
            print "Opening %s in your browser" % auth_url
        except:
            print "Please navigate here: %s" % auth_url
        response = raw_input("Enter the URL you were redirected to: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None

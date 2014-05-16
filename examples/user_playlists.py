# shows a user's playlists (need to be authenticated via oauth)

import pprint
import sys

import spotipy
import oauth2

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
	print "Whoops, need your username!"
	print "usage: python user_playlists.py [username]"
    sys.exit()

# Create these via developer.spotify.com/my-applications

client_id = ''
client_secret = ''
redirect_uri = ''

# Oauth flow
sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri)
auth_url = sp_oauth.get_authorize_url()
print "Please navigate here: %s" % auth_url
response = raw_input("The URL you were redirected to: ")
code = sp_oauth.parse_response_code(response)
access_token = sp_oauth.get_access_token(code)

# Auth'ed API request

sp = spotipy.Spotify(auth=access_token)
playlists = sp.user_playlists(username)
pprint.pprint(playlists)
# shows a user's playlists (need to be authenticated via oauth)

import pprint
import sys
import os
import subprocess

import spotipy

import spotipy.util as util


if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Whoops, need your username!")
    print("usage: python user_playlists.py [username]")
    sys.exit()

token = util.prompt_for_user_token(username)

if token:
    sp = spotipy.Spotify(auth=token)
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        print(playlist['name'])
else:
    print("Can't get token for", username)

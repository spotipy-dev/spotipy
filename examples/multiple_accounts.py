from pprint import pprint

import spotipy
import spotipy.util as util

while True:
    username = input("Type the Spotify user ID to use: ")
    token = util.prompt_for_user_token(username, show_dialog=True)
    sp = spotipy.Spotify(token)
    pprint(sp.me())

import spotipy
import spotipy.util as util

from pprint import pprint

while True:
    username = input("Type the Spotify user ID to use: ")
    token = util.prompt_for_user_token(username, show_dialog=True)
    sp = spotipy.Spotify(token)
    pprint(sp.me())
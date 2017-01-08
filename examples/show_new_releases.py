# shows artist info for a URN or URL

import spotipy
import sys
import pprint
import spotipy.util as util

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Whoops, need your username!")
    print("usage: python new_releases.py [username]")
    sys.exit()

token = util.prompt_for_user_token(username)

if token:
    sp = spotipy.Spotify(auth=token)

    response = sp.new_releases()

    while response:
        albums = response['albums']
        for i, item in enumerate(albums['items']):
            print(albums['offset'] + i,item['name'])

        if albums['next']:
            response = sp.next(albums)
        else:
            response = None
else:
    print("Can't get token for", username)

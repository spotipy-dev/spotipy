# shows a user's starred playlist

import sys
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
    results = sp.user_playlist(username)
    tracks = results['tracks']
    which = 1
    while tracks:
        for item in tracks['items']:
            track = item['track']
            print(which, track['name'], ' --', track['artists'][0]['name'])
            which += 1
        tracks = sp.next(tracks)

else:
    print("Can't get token for", username)

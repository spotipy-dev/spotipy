# shows a user's playlists (need to be authenticated via oauth)

import pprint
import sys
import os
import subprocess

import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util as util


def show_tracks(results):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print "   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Whoops, need your username!"
        print "usage: python user_playlists.py [username]"
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        top = 40
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        # pprint.pprint(playlists)
        matches = 0
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                print
                print playlist['name']
                print '  total tracks', playlist['tracks']['total']
                results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                # pprint.pprint(results)
                show_tracks(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    show_tracks(tracks)
                # pprint.pprint(results)
                matches += 1
                if matches >= top:
                    break
    else:
        print "Can't get token for", username


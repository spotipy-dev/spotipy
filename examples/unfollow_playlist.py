import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger('examples.unfollow_playlist')
logging.basicConfig(level='DEBUG')

'''
Spotify doesn't have a dedicated endpoint for deleting a playlist. However,
unfollowing a playlist has the effect of deleting it from the user's account.
When a playlist is removed from the user's account, the system unfollows it,
and then no longer shows it in playlist list.'''


def get_args():
    parser = argparse.ArgumentParser(description='Unfollows a playlist')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Playlist id')
    return parser.parse_args()


def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    sp.current_user_unfollow_playlist(args.playlist)


if __name__ == '__main__':
    main()

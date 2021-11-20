import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger('examples.delete_playlist')
logging.basicConfig(level='DEBUG')


def get_args():
    parser = argparse.ArgumentParser(description='Deletes a playlist for user')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Playlist id')
    return parser.parse_args()


def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    sp.current_user_unfollow_playlist(args.playlist)


if __name__ == '__main__':
    main()

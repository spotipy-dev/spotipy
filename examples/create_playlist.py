# Creates a playlist for a user
import argparse
import logging
import os

import spotipy
import spotipy.util as util

logger = logging.getLogger('examples.create_playlist')
logging.basicConfig(level='DEBUG')


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user')
    parser.add_argument('-u', '--username', required=False,
                        default=os.environ.get('SPOTIPY_CLIENT_USERNAME'),
                        help='Username id. Defaults to environment var')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Name of Playlist')
    parser.add_argument('-d', '--description', required=False, default='',
                        help='Description of Playlist')
    return parser.parse_args()


def main():
    args = get_args()
    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(args.username, scope)

    if token:
        logger.info('USERNAME: %s, PLAYLIST: %s', args.username, args.playlist)
        sp = spotipy.Spotify(auth=token)
        sp.user_playlist_create(args.username, args.playlist)
    else:
        logger.error("Can't get token for: %s", args.username)


if __name__ == '__main__':
    main()

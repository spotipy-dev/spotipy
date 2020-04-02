import argparse
import logging
import os

import spotipy
import spotipy.util as util

logger = logging.getLogger('examples.add_a_saved_album')
logging.basicConfig(level='DEBUG')

scope = 'user-library-modify'


def get_args():
    parser = argparse.ArgumentParser(description='Creates a playlist for user')
    parser.add_argument('-u', '--username', required=False,
                        default=os.environ.get('SPOTIPY_CLIENT_USERNAME'),
                        help='Username id. Defaults to environment var')
    parser.add_argument('-a', '--aids', action='append',
                        required=True, help='Album ids')
    return parser.parse_args()


def main():
    args = get_args()
    token = util.prompt_for_user_token(args.username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.current_user_saved_albums_add(albums=args.aids)
    else:
        logger.error("Can't get token for %s", args.username)


if __name__ == '__main__':
    main()

import argparse
import logging
import os

import spotipy
import spotipy.util as util

scope = 'user-library-modify'

logger = logging.getLogger('examples.add_a_saved_track')
logging.basicConfig(level='DEBUG')


def get_args():
    parser = argparse.ArgumentParser(description='Add tracks to Your '
                                     'Collection of saved tracks')
    parser.add_argument('-u', '--username', required=False,
                        default=os.environ.get('SPOTIPY_CLIENT_USERNAME'),
                        help='Username id. Defaults to environment var')
    parser.add_argument('-t', '--tids', action='append',
                        required=True, help='Track ids')
    return parser.parse_args()


def main():
    args = get_args()
    token = util.prompt_for_user_token(args.username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.current_user_saved_tracks_add(tracks=args.tids)
    else:
        logger.error("Can't get token for %s", args.username)


if __name__ == '__main__':
    main()

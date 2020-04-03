import argparse
import logging
import os

import spotipy
import spotipy.util as util

logger = logging.getLogger('examples.add_tracks_to_playlist')
logging.basicConfig(level='DEBUG')
scope = 'playlist-modify-public'


def get_args():
    parser = argparse.ArgumentParser(description='Adds track to user playlist')
    parser.add_argument('-u', '--username', required=False,
                        default=os.environ.get('SPOTIPY_CLIENT_USERNAME'),
                        help='Username id. Defaults to environment var')
    parser.add_argument('-t', '--tids', action='append',
                        required=True, help='Track ids')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Playlist to add track to')
    return parser.parse_args()


def main():
    args = get_args()
    token = util.prompt_for_user_token(args.username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.user_playlist_add_tracks(args.username, args.playlist, args.tids)
    else:
        logger.error("Can't get token for %s", args.username)


if __name__ == '__main__':
    main()

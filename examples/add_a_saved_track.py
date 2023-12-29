# code example that demonstrates current_user_saved_tracks_add(tracks=None) functionality
# Link to documentation -> https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.current_user_saved_tracks_add

import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-modify'

logger = logging.getLogger('examples.add_a_saved_track')
logging.basicConfig(level='DEBUG')


def get_args():
    parser = argparse.ArgumentParser(description='Add tracks to Your '
                                     'Collection of saved tracks')
    parser.add_argument('-t', '--tids', action='append',
                        required=True, help='Track ids')
    return parser.parse_args()


def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    sp.current_user_saved_tracks_add(tracks=args.tids)


if __name__ == '__main__':
    main()

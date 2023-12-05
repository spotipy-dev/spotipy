"""
Module Docstring needed
"""

import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger('examples.add_a_saved_album')
logging.basicConfig(level='DEBUG')

scope = 'user-library-modify'


def get_args():
    """
    Docstring needed
    """
    parser = argparse.ArgumentParser(description='Creates a playlist for user') # description here seems incorrect
    parser.add_argument('-a', '--aids', action='append',
                        required=True, help='Album ids')
    return parser.parse_args()


def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.current_user_saved_albums_add(albums=args.aids)


if __name__ == '__main__':
    main()

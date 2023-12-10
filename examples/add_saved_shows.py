"""
Add shows to current user's library
Usage: add_saved_shows.py -s show_id show_id ...
"""

import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-modify'

def get_args():
    parser = argparse.ArgumentParser(description='Add shows to library')
    # Default args set to Radiolab and 99% invisible
    parser.add_argument('-s', '--sids', nargs='+',
                        default=['2hmkzUtix0qTqvtpPcMzEL', '2VRS1IJCTn2Nlkg33ZVfkM'],
                        help='Show ids')
    return parser.parse_args()

def main():
    args = get_args()
    print('Adding following show ids to library: ' + str(args.sids))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.current_user_saved_shows_add(shows=args.sids)


if __name__ == '__main__':
    main()

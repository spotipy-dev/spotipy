"""
Check if shows are saved in user's library
Usage: check_show_is_saved -s show_id show_id ...
"""

import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'

def get_args():
    parser = argparse.ArgumentParser(description='Check that a show is saved')
    # Default args set to Radiolab and 99% invisible
    parser.add_argument('-s', '--sids', nargs='+',
                        default=['2hmkzUtix0qTqvtpPcMzEL', '2VRS1IJCTn2Nlkg33ZVfkM'],
                        help='Show ids')
    return parser.parse_args()

def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_saved_episodes_contains(episodes=args.sids)
    show_names = sp.shows(shows=args.sids)
    # Print show names and if show is saved by current user
    for i, show in enumerate(show_names['shows']):
        print(show['name'] + ': ' + str(results[i]))


if __name__ == '__main__':
    main()

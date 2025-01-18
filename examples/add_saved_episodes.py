"""
Add episodes to current user's library
Usage: add_saved_episodes.py -e episode_id episode_id ...
"""

import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-modify'

def get_args():
    parser = argparse.ArgumentParser(description='Add episodes to library')
    # Default args set to This American Life episodes 814 and 815
    parser.add_argument('-e', '--eids', nargs='+',
                        default=['6rxg9Lpt2ywNHFea8LxEBO', '7q8or6oYYRFQFYlA0remoy'],
                        help='Episode ids')
    return parser.parse_args()

def main():
    args = get_args()
    print('Adding following episode ids to library: ' + str(args.eids))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.current_user_saved_episodes_add(episodes=args.eids)


if __name__ == '__main__':
    main()
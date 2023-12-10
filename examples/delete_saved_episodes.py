"""
Delete episodes from current user's library
Usage: delete_saved_episodes.py -e episode_id episode_id ...
"""

import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-modify'

def get_args():
    parser = argparse.ArgumentParser(description='Delete episodes from library')
    # Default args set to This American Life episodes 814 and 815
    parser.add_argument('-e', '--eids', nargs='+',
                        default=['6rxg9Lpt2ywNHFea8LxEBO', '7q8or6oYYRFQFYlA0remoy'],
                        help='Episode ids')
    return parser.parse_args()

def main():
    args = get_args()
    print('Deleting following episode ids from library: ' + str(args.eids))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.current_user_saved_episodes_delete(episodes=args.eids)


if __name__ == '__main__':
    main()
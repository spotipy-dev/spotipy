"""
List current user's saved episodes
Usage: user_saved_episodes -l <num> -o <num>
"""

import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read'

def get_args():
    parser = argparse.ArgumentParser(description='Show user\'s saved episodes')
    parser.add_argument('-l', '--limit', default=20, help='Num of episodes to return')
    parser.add_argument('-o', '--offset', default=0, help='Index of first show to return')

    return parser.parse_args()

def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    results = sp.current_user_saved_episodes(limit=args.limit, offset=args.offset)
    # Print episode names
    for item in results['items']:
        print(item['episode']['name'])


if __name__ == '__main__':
    main()
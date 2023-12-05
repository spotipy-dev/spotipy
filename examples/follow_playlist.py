import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-modify-public' # Scope needs to be specified. I received an insufficient client scope error when I initially ran this script. This seemed to fix the issue.
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope)) # I would auth maanger here for readability. sp.<method> is much cleaner that what you had previously. Also make sure the scope is specified.


def get_args():
    parser = argparse.ArgumentParser(description='Follows a playlist based on playlist ID')
    parser.add_argument('-p', '--playlist', required=True, help='Playlist ID')

    return parser.parse_args()


def main():
    args = get_args()

    if args.playlist is None:
        # Uses the Spotify Global Top 50 playlist
        sp.current_user_follow_playlist(
            '37i9dQZEVXbMDoHDwVN2tF')

    else:
        sp.current_user_follow_playlist(args.playlist)


if __name__ == '__main__':
    main()

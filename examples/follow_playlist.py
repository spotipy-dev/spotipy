import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_args():
    parser = argparse.ArgumentParser(description='Follows a playlist based on playlist ID')
    parser.add_argument('-p', '--playlist', required=True, help='Playlist ID')

    return parser.parse_args()


def main():
    args = get_args()
    # Uses Lofi Girl playlist
    playlist = args.playlist or '0vvXsWCC9xrXsKd4FyS8kM'
    spotipy.Spotify(auth_manager=SpotifyOAuth()).current_user_follow_playlist(playlist)


if __name__ == '__main__':
    main()

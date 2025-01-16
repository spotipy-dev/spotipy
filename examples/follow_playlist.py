# Follow a playlist

import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_args():
    parser = argparse.ArgumentParser(description='Follows a playlist based on playlist ID')
    # Default to Top 50 Global if no playlist is provided
    parser.add_argument('-p', '--playlist', help='Playlist ID', nargs='?', default='37i9dQZEVXbMDoHDwVN2tF')
    return parser.parse_args()


def main():
    args = get_args()
    # Uses Lofi Girl playlist
    playlist = args.playlist or '0vvXsWCC9xrXsKd4FyS8kM'
    spotipy.Spotify(auth_manager=SpotifyOAuth()).current_user_follow_playlist(playlist)

if __name__ == '__main__':
    main()
import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_args():
    parser = argparse.ArgumentParser(description='Follows a playlist based on playlist ID')
    parser.add_argument('-p', '--playlist', required=True, help='Playlist ID')
    
    return parser.parse_args()

def main():
    args = get_args()
    
    if args.playlist is None:
      # Uses the Spotify Global Top 50 playlist
      spotipy.Spotify(auth_manager=SpotifyOAuth()).current_user_follow_playlist('37i9dQZEVXbMDoHDwVN2tF')
      
    else:
      spotipy.Spotify(auth_manager=SpotifyOAuth()).current_user_follow_playlist(args.playlist)
    
if __name__ == '__main__':
    main()

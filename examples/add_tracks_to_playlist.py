# code example that demonstrates playlist_add_items(playlist_id, items, position=None) functionality
# Link to documentation -> https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.playlist_add_items

import argparse
import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger('examples.add_tracks_to_playlist')
logging.basicConfig(level='DEBUG')
scope = 'playlist-modify-public'


def get_args():
    parser = argparse.ArgumentParser(description='Adds track to user playlist')
    parser.add_argument('-u', '--uris', action='append',
                        required=True, help='Track ids')
    parser.add_argument('-p', '--playlist', required=True,
                        help='Playlist to add track to')
    return parser.parse_args()


def main():
    args = get_args()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    sp.playlist_add_items(args.playlist, args.uris)


if __name__ == '__main__':
    main()

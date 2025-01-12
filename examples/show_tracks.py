'''
    usage: show_tracks.py path_of_ids

    given a list of track IDs show the artist and track name
'''
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='Print artist and track name given a list of track IDs')
    parser.add_argument('-u', '--uris', nargs='+',
                        required=True, help='Track ids')
    return parser.parse_args()


def main():
    args = get_args()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    track_list = sp.tracks(args.uris)
    for track in track_list['tracks']:
        print(track['name'] + ' - ' + track['artists'][0]['name'])


if __name__ == '__main__':
    main()

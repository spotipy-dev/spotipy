"""
Print chapter titles and lengths for given audiobook
Usage: get_audiobooks_chapters_info.py -a audiobook_id
"""

import argparse

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_args():
    parser = argparse.ArgumentParser(description='Get chapter info for an audiobook')
    # Default set to Dune
    parser.add_argument('-a', '--audiobook', default='2h01INWMBvfpzNMpGFzhdF', help='Audiobook id')
    return parser.parse_args()


def main():
    args = get_args()
    print('Getting chapter info for follow audiobook id: ' + str(args.audiobook))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    results = sp.get_audiobook_chapters(id=args.audiobook)
    # Print chapter name and length
    for item in results['items']:
        print('Name: ' + item['name'] + ', length: ' + str(round(item['duration_ms']/60000,1)) + ' minutes')


if __name__ == '__main__':
    main()
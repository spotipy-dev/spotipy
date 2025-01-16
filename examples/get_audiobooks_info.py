"""
Print audiobook title and description for a list of audiobook ids
Usage: get_audiobooks_info.py -a audiobook_id audiobook_id ...
"""

import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_args():
    parser = argparse.ArgumentParser(description='Get information for a list of audiobooks')
    # Defaults set to The Great Gatsby, The Chronicles of Narnia and Dune
    parser.add_argument('-a', '--aids', nargs='+',
                        default=['6qjpt1CUHhKXiNoeNoU7nu', '1ezmXd68LbDtxebvygEQ2U', '2h01INWMBvfpzNMpGFzhdF'],
                        help='Audiobook ids')
    return parser.parse_args()

def main():
    args = get_args()
    print('Getting info for follow audiobook ids: ' + str(args.aids) + '\n')
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth())
    results = sp.get_audiobooks(ids=args.aids)
    # Print book title and description
    for book in results['audiobooks']:
        print('Title: ' + book['name'] + '\n' + book['description'] + '\n')


if __name__ == '__main__':
    main()
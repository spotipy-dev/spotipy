# Extracts Taylor Swift's song titles, album titles, and URIs
import argparse
import json
import logging
import pandas as pd
import os
import spotipy
import sys

from collections import defaultdict
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

logger = logging.getLogger("examples.artist_discography")
logging.basicConfig(level="INFO")


def add_singles():
    singles_data = {"album": ["1989 (Taylor's Version)", "1989 (Taylor's Version)"], "title": ["Wildest Dreams (Taylor's Version)", "This Love (Taylor's Version)"], "track_number": [9, 11], "uri":["spotify:track:6QxwweFPcUgCZwYauDmjrj", "spotify:track:4d1CG5ei1E2vGbvmgf5KKv"]}
    singles_df = pd.DataFrame(data=singles_data)
    print(singles_df.head())

    return singles_df


def get_args():
    parser = argparse.ArgumentParser(
        description="Downloads Taylor Swift's discography and exports to a DataFrame and CSV"
    )
    parser.add_argument(
        "-a", "--artist", required=False, default="Taylor Swift", help="Name of Artist"
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        required=False,
        help="Output directory",
    )
    return parser.parse_args()


def get_artist(name):
    results = sp.search(q="artist:" + name, type="artist")
    items = results["artists"]["items"]
    print(items[0]['uri'])
    if len(items) > 0:
        return items[0]
    else:
        return None


def get_album_tracks(album):
    tracks = []
    results = sp.album_tracks(album["id"])
    tracks.extend(results["items"])
    taylors_songs = defaultdict(list)
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    for i, track in enumerate(tracks):
        album_title = album["name"]
        title = track["name"]
        track_number = track["track_number"]
        uri = track["uri"]
        taylors_songs["album"].append(album_title)
        taylors_songs["title"].append(title)
        taylors_songs["track_number"].append(track_number)
        taylors_songs["uri"].append(uri)
    album_df = pd.DataFrame(taylors_songs)
    return album_df


def show_artist_albums(artist):
    dfs = []
    albums = []
    results = sp.artist_albums(artist["id"], album_type="album")
    albums.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])
    logger.info("Total albums: %s", len(albums))
    unique = set()  # skip duplicate albums
    for album in albums:
        name = album["name"].lower()
        if name not in unique:
            logger.info("ALBUM: %s", name)
            unique.add(name)
            album_df = get_album_tracks(album)
            dfs.append(album_df)
    singles_df = add_singles()
    dfs.append(singles_df)
    discography_df = pd.concat(dfs)
    return discography_df


def main():
    args = get_args()
    artist = get_artist(args.artist)
    print(f'Downloading {artist} discography and exporting to CSV')
    discography_df = show_artist_albums(artist)
    if args.output_dir is None:
        output_path = "Taylor_Swift_songs.csv"
    else:
        output_path = os.path.join(args.output_dir, "Taylor_Swift_songs.csv")
    discography_df.to_csv(output_path, index=False)

    return discography_df


if __name__ == "__main__":
    main()


'''
'name': 'Wildest dreams (Taylor’s version)',
                       'popularity': 0,
                       'preview_url': 'https://p.scdn.co/mp3-preview/4e6636eaada74c2ace899478066a832fec5bbf2d?cid=695e0897e87a47d799ce3139b34debec',
                       'track_number': 14,
                       'type': 'track',
                       'uri': 'spotify:track:6QxwweFPcUgCZwYauDmjrj'},
                      {'album': {'album_type': 'single',

'href': 'https://api.spotify.com/v1/tracks/4d1CG5ei1E2vGbvmgf5KKv',
                       'id': '4d1CG5ei1E2vGbvmgf5KKv',
                       'is_local': False,
                       'name': 'This Love (Taylor’s Version)',
                       'popularity': 76,
                       'preview_url': 'https://p.scdn.co/mp3-preview/b52839c787d87a195922dd4dd436d92f38af79b9?cid=695e0897e87a47d799ce3139b34debec',
                       'track_number': 1,
                       'type': 'track',
                       'uri': 'spotify:track:4d1CG5ei1E2vGbvmgf5KKv'}],
'''
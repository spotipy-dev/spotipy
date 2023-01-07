"""
Script to Swiftly update your playlists with Taylor Swift's Re-Recordings 
last updated: 01/07/23
"""
import argparse
import ftfy
import json
import logging
import pandas as pd
import numpy as np
import os
import re
import spotipy

import sys

from collections import defaultdict
from spotipy.oauth2 import SpotifyOAuth
from pathlib import Path
from pprint import pprint

from taylor_tracks import main as get_taylor_tracks

scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

logger = logging.getLogger("examples.artist_discography")
logging.basicConfig(level="INFO")


def get_args():
    parser = argparse.ArgumentParser(
        description="SWIFTLY updates user playlists with Taylor's Version of songs (where applicable)"
    )
    parser.add_argument(
        "-p",
        "--playlist_id",
        required=False,
        help="URI for playlist you would like to update",
    )
    return parser.parse_args()


def create_song_mapping(args):
    discography_df = get_taylor_tracks()
    # Remove Karaoke tracks
    discography_df = discography_df[
        ~discography_df["album"].str.contains("karaoke|Karaoke")
    ]

    # Filter albums that have been re-recorded
    rerecords = discography_df["album"].str.contains(
        "fearless|Fearless|red|Red|Taylor's Version|1989"
    )
    df = discography_df[rerecords]
    df = identify_era(df)

    mapping_df = map_to_taylors_versions(df)

    return mapping_df


def get_user_playlists(args, username):
    print("Getting user playlist info")
    playlists = sp.user_playlists(username)
    playlist_dict = {}

    for playlist in playlists["items"]:
        name = playlist["name"]
        uri = playlist["uri"]
        owner = playlist["owner"]["id"]
        if owner == str(username):
            playlist_dict[uri] = name
        else:
            pass

    return playlist_dict


def identify_era(df):
    """
    Identify the TS era based on the album name
    """
    df["album_identifier"] = df["album"].str.replace(".", "")
    df["album_identifier"] = df["album_identifier"].str.replace(
        r" \(Taylor\'s Version\)", ""
    )
    df["album_identifier"] = df["album_identifier"].transform(
        lambda x: x.split("(", 1)[0]
    )
    df["album_identifier"] = df["album_identifier"].transform(
        lambda x: x.split("-", 1)[0]
    )
    df["album_identifier"] = df["album_identifier"].transform(lambda x: x.lower())
    df["album_identifier"] = np.where(
        df["title"].str.contains(
            "This Love|this love|Wildest Dreams|wildest dreams|Wildest dreams"
        ),
        "1989",
        df["album_identifier"],
    )
    df["album_identifier"] = df["album_identifier"].str.replace("platinum edition", "")
    df["album_identifier"] = df["album_identifier"].str.replace("deluxe edition", "")
    df["album_identifier"] = df["album_identifier"].transform(lambda x: x.strip())

    return df


def map_to_taylors_versions(df):
    df["title"] = df["title"].transform(lambda x: ftfy.fix_encoding(x))
    df["title"] = df["title"].str.replace(".", "")
    keith_urban_title = (
        "That's When (feat Keith Urban) (Taylor's Version) (From The Vault)"
    )
    df["title"] = np.where(
        df["title"].str.contains("Keith Urban"), keith_urban_title, df["title"]
    )
    df["simple_title"] = df["title"].str.replace(r" \(Taylor\'s Version\)", "")
    df["simple_title"] = df["simple_title"].transform(lambda x: x.split("(", 1)[0])
    df["simple_title"] = df["simple_title"].transform(lambda x: x.split("-", 1)[0])
    df["simple_title"] = df["simple_title"].transform(lambda x: x.strip())
    df["simple_title"] = df["simple_title"].transform(lambda x: x.lower())
    df["simple_title"] = np.where(
        df["simple_title"].str.contains("not sorry"),
        "you're not sorry",
        df["simple_title"],
    )

    # Identify which albums are owned by Big Red Machine vs. Taylor's Version
    brm_df = df[~df["album"].str.contains("Taylor's Version")]
    taylors_version = df["album"].str.contains("Taylor's Version")
    tv_df = df[taylors_version]

    brm_df.rename(columns={"album": "stolen_album"}, inplace=True)
    tv_df.rename(columns={"title": "taylor's_title"}, inplace=True)
    tv_df.rename(columns={"album": "taylor's_album"}, inplace=True)
    tv_df.rename(columns={"uri": "tv_uri"}, inplace=True)
    merged_df = pd.merge(
        brm_df, tv_df, on=["simple_title", "album_identifier"], how="outer"
    )
    merged_df.sort_values(
        ["simple_title", "album_identifier"], ascending=True, inplace=True
    )

    return merged_df


def replace_tracks(mapping_df, playlist_id, username):
    # Store mapping in a DataFrame and dictionary
    print("Scanning playlist: ", playlist_id)
    mapping_df.dropna(inplace=True)
    uri_dict = dict(zip(mapping_df.uri, mapping_df.tv_uri))
    stolen_versions = list(uri_dict.keys())

    offset = 0
    playlist_ids = []
    while True:
        response = sp.playlist_items(
            playlist_id,
            offset=offset,
            additional_types=["track"],
        )
        items = response["items"]
        if len(items) == 0:
            break
        offset = offset + len(response["items"])
        print(offset, "/", response["total"])
        for item in items:
            try:
                title = item["track"]["name"]
                track_number = item["track"]["track_number"]
                uri = item["track"]["uri"]
                if uri in stolen_versions:
                    tracks_to_remove = [uri]
                    sp.playlist_remove_all_occurrences_of_items(
                        playlist_id, tracks_to_remove
                    )
                    print(f"Removing {title} from playlist")
                    tv_uri = uri_dict.get(uri)
                    if tv_uri not in playlist_ids:
                        tracks_to_add = [tv_uri]
                        sp.playlist_add_items(
                            playlist_id, tracks_to_add, position=track_number
                        )
                        print("Added Taylor's Version to playlist")
                    else:
                        pass
                else:
                    playlist_ids.append(uri)
            except TypeError:
                print("Error processing playlist", playlist_id)
    print("Done reviewing this playlist.")


def main():
    args = get_args()
    artist = "Taylor Swift"
    username = input("Enter your spotify username")
    username = str(username)

    # Create mapping of stolen versions to Taylor's Versions
    mapping_df = create_song_mapping(args)

    # Identify playlist IDs
    if args.playlist_id is not None:
        playlist_id = args.playlist_id
        replace_tracks(mapping_df, playlist_id, username)
        print("Done")
    else:
        playlist_dict = get_user_playlists(args, username)
        playlist_ids = list(playlist_dict.keys())
        print(playlist_ids)
        for playlist_id in playlist_ids:
            playlist_name = playlist_dict.get(playlist_id)
            print(f"*****{playlist_name}******")
            replace_tracks(mapping_df, playlist_id, username)
        print("You will now be listening to Taylor's Versions on playlists you own!")


if __name__ == "__main__":
    main()

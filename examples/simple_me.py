from pprint import pprint

import spotipy


def main():
    spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth())
    me = spotify.me()
    pprint(me)


if __name__ == "__main__":
    main()

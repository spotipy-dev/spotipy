import spotipy
from pprint import pprint


def main():
    spotify = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth())
    me = spotify.me()
    pprint(me)


if __name__ == "__main__":
    main()

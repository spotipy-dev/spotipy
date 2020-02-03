import spotipy
import os
from pprint import pprint

def main():
    auth_manager = spotipy.SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        username=os.getenv("SPOTIPY_CLIENT_USERNAME"),
    )
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    me = spotify.me()
    pprint(me)

if __name__ == "__main__":
    main()

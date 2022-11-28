import spotipy

from spotipy.oauth2 import SpotifyOAuth

# set open_browser=False to prevent Spotipy from attempting to open the default browser
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(open_browser=False))

print(spotify.me())
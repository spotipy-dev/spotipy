import spotipy

from spotipy.oauth2 import SpotifyOAuth

# set open_browser=False to prevent Spotipy from attempting to open the default browser
# Note that some browsers might hide the URL redirected to, if this happens test another browser
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(open_browser=False))

print(spotify.me())

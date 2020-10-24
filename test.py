import spotipy
from pprint import pprint
# Spotify init
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(scope='playlist-modify-public playlist-modify-private',
                                                       show_dialog=True))
playlist = sp.album("0sNOF9WDwhWunNAHPD3Baj")

pprint(playlist['label'])

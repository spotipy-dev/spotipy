
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read user-top-read playlist-modify-public"
ranges = ['short_term', 'medium_term', 'long_term']

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = "326a452a53254fa9bc90368567c70861", client_secret = "7d518966cb804f019a4301db077c1c31", redirect_uri = "http://localhost:8888/callback", scope = scope))

# Shows the top artists for a user
def get_top_artists(sp):
    
    top_artists = sp.current_user_top_artists(time_range = "short_term", limit = 15)
    return top_artists['items']

# gets top tracks for the user
def get_top_tracks(sp, top_artists):
    
    top_tracks_uri = []
    for i in top_artists:
        top_tracks_all_data = sp.artist_top_tracks(i)
        top_tracks_data = top_tracks_all_data['tracks']
        for track_data in top_tracks_data:
            top_tracks_uri.append(track_data['uri'])
    
    return top_tracks_uri

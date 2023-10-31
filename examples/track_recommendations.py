import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

# Set up Spotify credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_APP_CLIENT_ID",
    client_secret="YOUR_APP_CLIENT_SECRET",
    redirect_uri="YOUR_APP_REDIRECT_URI",
    scope="user-top-read,user-library-read,user-read-recently-played"))

# Get the user's top tracks
top_tracks = sp.current_user_top_tracks(limit=10, time_range='long_term')

# Get the user's liked tracks
liked_tracks = sp.current_user_saved_tracks(limit=10)

# Get the user's listening history
history = sp.current_user_recently_played(limit=10)

# Extract a list of the top track IDs
top_track_ids = [track['id'] for track in top_tracks['items']]

# Extract a list of the liked track IDs
liked_track_ids = [track['track']['id'] for track in liked_tracks['items']]

# Extract a list of the history track IDs
history_track_ids = [track['track']['id'] for track in history['items']]

# Combine the three lists and shuffle them randomly
seed_track_ids = top_track_ids + liked_track_ids + history_track_ids
random.shuffle(seed_track_ids)

# Use the IDs to get some recommendations
# Note: the seed_tracks parameter can accept up to 5 tracks
recommendations = sp.recommendations(
    seed_tracks=seed_track_ids[0:5], limit=10, country='US')

# Display the recommendations
for i, track in enumerate(recommendations['tracks']):
    print(
        "{}. {} by {}"
        .format(i+1, track['name'], ', '
                .join([artist['name'] for artist in track['artists']]))
    )

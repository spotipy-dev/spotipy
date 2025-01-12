import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Import the extra necessary libraries for this example
# These libraries are not included in the default packages
import pandas as pd
from sklearn.cluster import KMeans

# Set up Spotify credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_APP_CLIENT_ID",
    client_secret="YOUR_APP_CLIENT_SECRET",
    redirect_uri="YOUR_APP_REDIRECT_URI",
    scope="playlist-modify-private,user-library-read"))


# get the user's username
username = sp.me()['id']

# Get the user's liked tracks
saved_tracks = sp.current_user_saved_tracks(limit=50)['items']

# Extract audio features for liked tracks
track_ids = []
audio_features = []
for track in saved_tracks:
    track_ids.append(track['track']['id'])
    audio_features.append(sp.audio_features(track['track']['id'])[0])

# Create a DataFrame from the audio features
df = pd.DataFrame(audio_features)

# Perform clustering on some audio features
features = df[['danceability', 'energy', 'valence', 'acousticness']]
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(features)

# Select a representative track from each cluster
representative_tracks = []
for cluster in range(5):
    cluster_tracks = df[df['cluster'] == cluster]
    representative_track = cluster_tracks.iloc[0]['id']
    representative_tracks.append(representative_track)

# Create a playlist with the representative tracks
playlist = sp.user_playlist_create(
    user=username, name='Personalized Playlist', public=False)
sp.playlist_add_items(
    playlist_id=playlist['id'], items=representative_tracks)

# Print the URL of the created playlist
print("Playlist created successfully. You can access it at:",
      playlist['external_urls']['spotify'])

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Import the extra necessary libraries for this example
# These libraries are not included in the default packages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up Spotify credentials
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Fetch audio features of tracks from any playlist
playlist_id = '37i9dQZEVXbMDoHDwVN2tF'
results = sp.playlist_tracks(playlist_id)
tracks = results['items']
track_ids = [track['track']['id'] for track in tracks]
audio_features = sp.audio_features(track_ids)

# Create a DataFrame of audio features
df = pd.DataFrame(audio_features)
df = df[['danceability', 'energy', 'speechiness', 'acousticness',
         'instrumentalness', 'liveness', 'valence', 'tempo']]

# Generate a correlation matrix
correlation_matrix = df.corr()

# Plot the correlation matrix using seaborn
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

# Show the plot
plt.show()

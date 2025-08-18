from typing import List, Dict, Optional
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_new_albums_by_genre_year(
    client_id: str,
    client_secret: str,
    genre: str,
    year: int,
    limit: int = 20
) -> List[Dict]:
    """
    Retrieve new albums for a specific genre starting from a given year.

    Args:
        client_id (str): Spotify API client ID
        client_secret (str): Spotify API client secret
        genre (str): Genre to filter by (e.g., 'pop', 'rock', 'jazz')
        year (int): Minimum release year (inclusive)
        limit (int, optional): Maximum number of results to return. Defaults to 20.

    Returns:
        List[Dict]: List of album dictionaries containing album information
    """
    # Set up Spotify client
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Get current year for the query
    current_year = datetime.now().year
    
    try:
        # Search for albums in the specified genre and year range
        results = sp.search(
            q=f'genre:"{genre}" year:{year}-{current_year}',
            type='album',
            limit=limit,
            market='US'  # You can make this a parameter if needed
        )
        
        # Extract and format album information
        albums = []
        for item in results['albums']['items']:
            album = {
                'name': item['name'],
                'artists': [artist['name'] for artist in item['artists']],
                'release_date': item['release_date'],
                'total_tracks': item['total_tracks'],
                'album_type': item['album_type'],
                'external_urls': item['external_urls']['spotify'],
                'id': item['id']
            }
            albums.append(album)
            
        return albums
        
    except Exception as e:
        print(f"Error fetching albums: {str(e)}")
        return []

# Example usage:
if __name__ == "__main__":
    # Replace these with your actual Spotify API credentials
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    
    # Example: Get rock albums from 2020 onwards
    albums = get_new_albums_by_genre_year(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        genre="rock",
        year=2020,
        limit=5
    )
    
    for album in albums:
        print(f"{album['name']} by {', '.join(album['artists'])} ({album['release_date']})")

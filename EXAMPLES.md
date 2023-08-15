## List of Example files for easier use/organization

### Albums

`add_a_saved_album.py`
- Saves an Album to the user's library
- Input: Album the user wants to save
- Output: Album is saved to their library

`show_album.py`
- Shows info for given Album
- Input: Album URL
- Output: Displays the Album's info, such as Album Type, Total Tracks, and Artist

`show_featured_artists.py`
- Shows all Artists featured on an Album
- Input: Album URL
- Output: All Artists featured on the given Album


### Artists

`artist_albums.py`
- Shows Albums from given Artist
- Input: Artist name
- Output: All albums created by the Artist

`artist_discography.py`
- Shows Tracks from given Artist
- Input: Artist name
- Output: All tracks created by the Artist

`artist_recommendations.py`
- Shows recommendations for the given Artist
- Input: Artist name
- Output: Recommended songs from the Artist

`audio_features.py`
- Shows audio features for given Artist
- Input: Artist name
- Output: Audio features such as Acousticness, Danceability, Energy, and Instrumentalness

`show_artist.py`
- Shows info for given Artist
- Input: Artist URL
- Output: Displays the Artist's info such as Follower Count, Popularity, and Genre

`show_artist_top_tracks.py`
- Shows the top Tracks by an Artist
- Input: Artist URL
- Output: Top Tracks by the given Artist

`show_featured_playlists.py`
- Shows the featured Albums by an Artist
- Input: Artist URL
- Output: Featured Albums from the given Artist

`show_new_releases.py`
- Shows the new releases from an Artist
- Input: Artist URL
- Output: New releases from the given Artist, or None if there are no new releases

`show_related.py`
- Shows similar Artists for a given Artist, used for recommendations
- Input: Artist Name
- Output: Related Artists for the given Artist

`simple_artist_albums.py`
- Shows Albums for given Artist
- Input: Artist ID
- Output: All Albums by given Artist

`simple_artist_top_tracks.py`
- Shows Top Tracks for given Artist
- Input: Artist ID
- Output: Track Name, Audio, and Cover Art for 10 of the Artist's Top Tracks

`tracks.py`
- Shows Tracks for the given Artist
- Input: Artist name
- Output: Up to 20 Tracks by the given Artist


### Player

`player.py`
- Plays the current Track
- Input: None
- Output: Shows playing devices, changes the track and volume


### Playlists

`add_tracks_to_playlist.py`
- Adds track to user's playlist
- Input: Track to add and Playlist to add it to
- Output: Track is added to the Playlist

`change_playlist_details.py`
- Changes description and details of given Playlist
- Input: Playlist ID to alter
- Optional: Change playlist Name, Public/Private, Collaboration, Description
- Output: Playlist is modified to user specifications

`create_playlist.py`
- Creates a playlist for user
- Input: Playlist name and description
- Output: New Playlist is created with given name and description

`follow_playlist.py`
- Follows a Playlist based on playlist ID
- Input: Playlist ID
- Output: Follows the given Playlist

`playlist_add_items.py`
- Adds a list of Tracks (URI) to a Playlist (URI)
- Input: Playlist ID, List of [Track ID]
- Output: Listed Tracks are added to given Playlist

`playlist_all_non_local_tracks.py`
- Shows all non-local Tracks of a Playlist
- Input: Playlist
- Output: Shows all non-local Tracks and Playlist length

`playlist_tracks.py`
- Shows all Tracks in a Playlist
- Input: Playlist ID
- Output: Shows all Tracks in given Playlist

`remove_specific_tracks_from_playlist.py`
- Removes a specific Track from a Playlist
- Used when multiple of the same Track exists, and user wants to remove some
- Input: Playlist ID, Track ID, Track Position
- Output: Only the given Track is removed from the Playlist

`remove_tracks_from_playlist.py`
- Removes all instances of a Track from a Playlist
- Used when multiple of the same Track exists, and user wants to remove all
- Input: Playlist ID, Track ID
- Output: All instances of given Track are removed from Playlist

`unfollow_playlist.py`
- Removes a Playlist from the user's account
- Input: Playlist ID
- Output: User no longer follows the given Playlist


### Search

`search.py`
- Searches for the given String, including Artists, Playlists, Tracks
- Input: Search query
- Output: Shows results relating to given String

`simple_search_artist.py`
- Searches for the given Artist
- Input: Artist name
- Output: 20 related Tracks for the given Artist

`simple_search_artist_image_url.py`
- Searches for the name of the Artist from a given link
- Input: Link for an Artist
- Output: Name and Images for the related Link

`title_chain.py`
- Generates a list of Tracks where the first word in each subsequent Track matches the last word of the previous Track
- An example of how Spotipy can be used for more complex features than the Spotify Web API
- Input: Track Name
- Output: A list of 20 'chained together' Tracks with their Artists


### Tracks

`add_a_saved_track.py`
- Adds a Track to user's 'Collection of saved tracks'
- Input: Track(s) the user wants to save
- Output: Track(s) are saved to their library

`audio_analysis_for_track.py`
- Shows the audio analysis for given Track
- Input: Track ID
- Output: Audio analysis such as Duration, Number of Audio Samples, Loudness, Tempo, and Time Signature

`audio_features_for_track.py`
- Shows the audio features for given track
- Input: Track ID
- Output: Audio features such as Acousticness, Danceability, Energy, and Instrumentalness

`delete_a_saved_track.py`
- Deletes a Track from user's 'Collection of saved tracks'
- Input: Track to be deleted
- Output: Track is removed from their library

`show_track_info.py`
- Shows information about a given track
- Input: Track URL
- Output: Gives info on Track, such as Artist, Album, and Popularity

`show_tracks.py`
- Shows info about given Tracks
- Input: Track IDs
- Output: List of Track names and Artists for given Track IDs


### Users

`my_playlists.py`
- Shows the user's current Playlists
- Input: None
- Output: Shows the name of the user's saved Playlists

`my_top_artists.py`
- Shows the user's top Artists in three time ranges
- Input: None
- Output: Shows the user's top 50 Artists in short, medium, and long term increments

`my_top_tracks.py`
- Shows the user's top Tracks in three time ranges
- Input: None
- Output: Shows the user's top 50 Tracks in short, medium, and long term increments

`show_my_saved_tracks.py`
- Shows the user's saved Tracks
- Input: None
- Output: Shows the Artist and Track name for user's saved Tracks

`user_playlists.py`
- Shows a given user's Playlists
- Input: Username
- Output: List of Playlists the given user follows

`user_playlists_contents.py`
- Shows the contents of current user's Playlists
- Input: None
- Output: List of Playlist contents for the current user

`user_public_playlists.py`
- Shows all public Playlists for given user
- Input: username
- Output: List of public Playlist URIs and Names for given user

`user_saved_albums_delete.py`
- Deletes an Album saved by the current user
- Input: Album URIs, URLs, or IDs
- Output: Deletes the given Album(s)

'''
As an alternative to exporting your credentials into the environment, 
you may chose to create a separate file, next to your main file, 
called credentials.py containing the following values:

# created at https://developer.spotify.com
SPOTIPY_CLIENT_ID='my client id'
SPOTIPY_CLIENT_SECRET='client secret'
SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080'

now you can import them into your app.

Be sure not to commit this file to a public remote!
Add it to your .gitignore file.
'''

import credentials

auth_manager = spotipy.oauth2.SpotifyOAuth(credentials.SPOTIPY_CLIENT_ID, 
                                            credentials.SPOTIPY_CLIENT_SECRET, 
                                            credentials.SPOTIPY_REDIRECT_URI, 
                                            scope='user-read-currently-playing', 
                                            show_dialog=True, 
                                            cache_path=CACHE)
											
spotify = spotipy.Spotify(auth_manager=auth_manager)

# do stuff
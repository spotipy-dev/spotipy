# Spotipy

##### A light weight Python library for the Spotify Web API

![Tests](https://github.com/plamere/spotipy/workflows/Tests/badge.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)

## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).

## Installation

```bash
pip install spotipy
```

or upgrade

```bash
pip install spotipy --upgrade
```

## Quick Start

A full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples).

To get started, install spotipy and create an app on https://developers.spotify.com/.

To create an app on https://developers.spotify.com/ and obtain the Client ID and Client Secret.
1. On the homepage, click on "Dashboard".
2. Login or create a Spotify account.
3. Click on "Create An App".
4. Click on your created app.
5. Copy the "Client ID" and "Client Secret".

Add your new ID and SECRET to your environment:

### Without user authentication

```python
"""
Importing allows the user to use Spotipy API to obtain a token from a Spotify profile to be used within the code
By using Spotipy, a user is able to obtain the necessary authentication information from a Spotify account and create
an object to be stored into a variable. 
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

"""
Without user authentication, the program immediately displays the information the program asks Spotify to provide. 
client_id and client_secret are the only information needed to access a Spotify account. Below Spotipy will obtain a token 
to authenticate and create an object the user can use. 
"""
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

"""
With the created object, now we can use Spotipy objects such as 
the "search" function in order to find specific artists like weezer    
It stores the information found into the results variable
"""
results = sp.search(q='weezer', limit=20) 

# This is a loop going through each song created by weezer stored in the result variable 
for idx, track in enumerate(results['tracks']['items']):  
    # Each loop the program will print a song name made by weezer
    print(idx, track['name'])
```

### With user authentication

```python
"""
These are libraries that will assist in the authentication process for the program and Spotify
It allows the user to use Spotipy API in order to obtain a token from the Spotify profile and be used within the code
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

"""
With Spotipy, A user is able to obtain the necessary authentication information from Spotify and create an object
that gives user access to Spotipy's functions. With user authentication, the program will redirect the user to a separate website 
and request the user to input the website web address to verify the user before printing the data. Scope determines
how much of the data the program can access.
"""
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope="user-library-read"))
"""
With the created object, now we can use the Spotipy functions such as the "current_user_saved_tracks()" in order to get all
the song information found in the Liked Song list of the Spotify account. The result will hold all the data gathered from the Liked Songs list
"""
results = sp.current_user_saved_tracks() 

"""
After authentication, the user is able to use the object
to get specific information from the results, this program will use a loop to go through each item found. 
"""

# This is a loop, going through each song in the Liked Song list
for idx, item in enumerate(results['items']): 
    # In each loop we a single track within the Liked Song list
    track = item['track']	
    # With the specific track found, this will find the name of the track and the artist
    print(idx, track['artists'][0]['name'], " – ", track['name']) 
```

## Reporting Issues

For common questions please check our [FAQ](FAQ.md).

You can ask questions about Spotipy on
[Stack Overflow](http://stackoverflow.com/questions/ask).
Don’t forget to add the *Spotipy* tag, and any other relevant tags as well, before posting.

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/plamere/spotipy/issues).
Or just send a pull request.

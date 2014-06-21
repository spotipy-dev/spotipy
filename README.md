# Spotipy - a Python client for The Spotify API

## Description

Spotipy is a thin client library for the Spotify Web API . 


## Installation
If you already have [Python](http://www.python.org/) on your system you can install
the library simply by downloading the distribution, unpack it and install in the usual fashion:

    python setup.py install

You can also install it using a popular package manager with 

  `pip install SpotipyWebAPI`

or

  `easy_install SpotipyWebAPI`


## Dependencies

- [Requests](https://github.com/kennethreitz/requests) - spotipy requires the requests package to be installed


## Quick Start
To get started:

- Install spotipy

- Create a Spotify object   
   
    sp = spotipy.Spotify()

Call methods:

	tracks = sp.search(q='weezer', limit=20)
    for i, t in enumerate(tracks['tracks']):
        print ' ', i, t['name']

A full set of examples can be found in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples)
        
   
## Supported Methods

  - **album(self, album_id)** - returns a single album given the album's ID, URN or URL
  - **album_tracks(self, album_id)** - Get Spotify catalog information about an album’s tracks
  - **albums(self, albums)** - returns a list of albums given the album IDs, URNs, or URLs
  - **artist(self, artist_id)** - returns a single artist given the artist's ID, URN or URL
  - **artist_albums(self, artist_id, album_type=None, country=None, limit=20, offset=0)** -      Get Spotify catalog information about an artist’s albums
  - **artist_top_tracks(self, artist_id, country='US')** - Get Spotify catalog information about an artist’s top 10 tracks by country.
  - **artists(self, artists)** - returns a list of artists given the artist IDs, URNs, or URLs
  - **me(self)** - returns info about me
  - **next(self, result)** - returns the next result given a result
  - **previous(self, result)** - returns the previous result given a result
  - **search(self, q, limit=10, offset=0, type='track')** - searches for an item
  - **track(self, track_id)** - returns a single track given the track's ID, URN or URL
  - **tracks(self, tracks)** - returns a list of tracks given the track IDs, URNs, or URLs
  - **user(self, user_id)** - Gets basic profile information about a Spotify User
  - **user_playlist(self, user, playlist_id=None, fields=None)** - Gets playlist of a user
  - **user_playlist_add_tracks(self, user, playlist_id, tracks, position=None)** - Adds tracks to a playlist
  - **user_playlist_create(self, user, name, public=True)** - Creates a playlist for a user
  - **user_playlists(self, user)** -      Gets playlists of a user

Refer to the [Spotify API documentation](https://developer.spotify.com/spotify-web-api/) for details on the methods and parameters.

Methods that take item IDs (such as the track, album and artist methods) accept URN, URL or simple ID types. The following 3 ids are all acceptable IDs:

        - http://open.spotify.com/track/3HfB5hBU0dmBt8T0iCmH42
        - spotify:track:3HfB5hBU0dmBt8T0iCmH42
        - 3HfB5hBU0dmBt8T0iCmH42


## Reporting Issues

If you have suggestions, bugs or other issues specific to this library, file them [here](https://github.com/plamere/spotipy/issues) or contact me
at [paul@echonest.com](mailto:paul@echonest.com). Or just send me a pull request.

## Version

- 1.0 - 04/05/2014 - Initial release
- 1.1 - 05/18/2014 - Repackaged for saner imports
- 1.4.1 - 06/17/2014 - Updates to match released API
- 1.4.2 - 06/21/2014 - Added support for retrieving starred playlists


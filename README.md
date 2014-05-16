# Spotipy - a Python client for The Spotify API

## Description

Spotipy is a thin client library for the Spotify Web API . 


## Installation
If you already have [Python](http://www.python.org/) on your system you can install
the library simply by downloading the distribution, unpack it and install in the usual fashion:

    python setup.py install


## Dependencies

- [Requests](https://github.com/kennethreitz/requests) - spotipy requires the requests package to be installed

## Limitations
This version of the library does not support user authentication



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

 - track - gets info for a single track
 - tracks - gets info for multiple tracks
 - album - gets info for a single album
 - albums - gets info for a set of albums 
 - artist - gets info for an artist
 - artists - gets info for a set of artists
 - artist_albums - gets info about an artist's albums
 - artist_top_tracks - gets info about an artist's top tracks
 - user - gets profile info for a user
 - search - searches for artists, albums or tracks

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
- 1.1 - 05/16/2014 - Adapt to web API changes. Early auth support.


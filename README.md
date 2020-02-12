# Spotipy

##### A light weight Python library for the Spotify Web API

![Tests](https://github.com/plamere/spotipy/workflows/Tests/badge.svg) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)

## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).

## Installation

    pip install spotipy

## Quick Start

A full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples).

To get started, install spotipy and create an app on https://developers.spotify.com/.
Add your new ID and SECRET to your environment:

    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here

    // on Windows, use `SET` instead of `export`).

Then, create a Spotify object and call methods:

    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    results = sp.search(q='weezer', limit=20)
    for idx, track in enumerate(results['tracks']['items']):
        print(idx, track['name'])

## Reporting Issues

If you have suggestions, bugs or other issues specific to this library, file them [here](https://github.com/plamere/spotipy/issues). Or just send me a pull request.

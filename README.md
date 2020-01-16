# Spotipy

##### A light weight Python library for the Spotify Web API

[![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)


## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).


## Installation
If you already have [Python](http://www.python.org/) on your system you can install the library simply by downloading the distribution, unpack it and install in the usual fashion:

```bash
python setup.py install
```

You can also install it using a popular package manager with

```bash
pip install spotipy
```

or

```bash
easy_install spotipy
```

## Dependencies

- [Requests](https://github.com/kennethreitz/requests) - spotipy requires the requests package to be installed


## Quick Start

A full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples). Here are two basic examples.

To get started, install spotipy and create an app on https://developers.spotify.com/.
Add your new ID and SECRET to your environment:

> export SPOTIPY_CLIENT_ID='your-spotify-client-id'
> export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'

Then, create a Spotify object and call methods:

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

results = sp.search(q='weezer', limit=20)
for i, t in enumerate(results['tracks']['items']):
    print(' ', i, t['name'])
```

## Reporting Issues

If you have suggestions, bugs or other issues specific to this library, file them [here](https://github.com/plamere/spotipy/issues). Or just send me a pull request.
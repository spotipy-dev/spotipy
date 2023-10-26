# Spotipy, A Python Library

Spotipy is a Python library for the Spotify Web API. This library is designed to simplify the interaction with the Spotify Web API, and the OAuth 2.0 authorization process. It allows requests to be made against Spotify's Web API for fetching information about: artists, albums, tracks, playlists, users, and much more. Addition information about this library can be found in the [Spotipy documentation](https://spotipy.readthedocs.io/en/latest/).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Reporting Issues](#reporting-issues)

## Features

- **Spotify Web API Interaction**: Spotipy enables you to interact with the Spotify Web API, including searching for tracks, albums, artists, and playlists, as well as managing user playlists and following artists. Documentation for the API can be found in the [Spotify Developer Portal](https://developer.spotify.com/documentation/web-api/).

- **Authentication**: Supports OAuth 2.0 authentication, making it easy to access user data and perform actions on behalf of the user.

- **Enpoint Access**: Spotipy supports all of the features of the Spotify Web API including access to all endpoints, and support for user authorization, and private playlists.

## Installation

You can install Spotipy using pip, the Python package manager. Python versions 2.7, 3.3+ are supported.
Simply run this command in a terminal:

```bash
pip install spotipy
```

## Getting Started

To get started, you'll need to register your application on the [Spotify Developer Website](https://developer.spotify.com/dashboard/applications). Once you've registered your application, you'll be provided with a Client ID and Client Secret. You'll need to set these as environment variables in your terminal session before running the examples below, replacing the values with your own.

```bash
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```

To use enviorment variables in your Python code, you can use the `os` module:

```python
import os
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')
```

## Usage

To use Spotipy <b>without</b> user authentication, import the library and create an instance of the `Spotify` class with your user credentials:

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
```

To use Spotipy <b>with</b> user authentication, import the library and create an instance of the `SpotifyOAuth` class with your user credentials:

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",      
                                        client_secret="YOUR_APP_CLIENT_SECRET",      
                                        redirect_uri="YOUR_APP_REDIRECT_URI",
                                        scope="user-library-read"))
```

## Examples

Complete API documentation, including code examples, is available on [Spotipy's Read the Docs page](https://spotipy.readthedocs.io/en/latest/).

### Search for an Item

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

result = sp.search(q='weezer', limit=20)
for i, t in enumerate(result['tracks']['items']):
    print(' ', i, t['name'])
```

### Get an Artist's Albums

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

results = spotify.artist_albums(birdy_uri, album_type='album')
albums = results['items']
while results['next']:
    results = spotify.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])
```

## Contributing

We welcome your contributions! This information should help you get started. Please see the [contribution guidelines](CONTRIBUTING.md) for more information and the [code of conduct](CODE_OF_CONDUCT.md) for guidance on acceptable behavior.

### Export the needed environment variables

```bash
# Linux or Mac
export SPOTIPY_CLIENT_ID=client_id_here
export SPOTIPY_CLIENT_SECRET=client_secret_here
export SPOTIPY_CLIENT_USERNAME=client_username_here # This is actually an id not spotify display name
export SPOTIPY_REDIRECT_URI=http://localhost:8080 # Make url is set in app you created to get your ID and SECRET

# Windows
$env:SPOTIPY_CLIENT_ID="client_id_here"
$env:SPOTIPY_CLIENT_SECRET="client_secret_here"
$env:SPOTIPY_CLIENT_USERNAME="client_username_here" 
$env:SPOTIPY_REDIRECT_URI="http://localhost:8080" 
```

### Create virtual environment, install dependencies, run tests

```bash
$ virtualenv --python=python3.7 env
$ source env/bin/activate
(env) $ pip install --user -e .
(env) $ python -m unittest discover -v tests
```

### Lint

To automatically fix the code style:

```bash
pip install autopep8
autopep8 --in-place --aggressive --recursive .
```

To verify the code style:

```bash
pip install flake8
flake8 .
```

To make sure if the import lists are stored correctly:

```bash
pip install isort
isort . -c -v
```

### Publishing (by maintainer)

- Bump version in setup.py
- Bump and date changelog
- Add to changelog:

```markdown
## Unreleased

// Add new changes below

### Added

### Fixed

### Removed
```

- Commit changes
- Package to pypi:

```bash
python setup.py sdist bdist_wheel
python3 setup.py sdist bdist_wheel
twine check dist/*
twine upload dist/*
```

- Create github release <https://github.com/plamere/spotipy/releases> with the changelog content
   for the version and a short name that describes the main addition
- Verify doc uses latest <https://readthedocs.org/projects/spotipy/>

### Changelog

Don't forget to add a short description of your change in the [CHANGELOG](CHANGELOG.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```markdown
MIT License

Copyright (c) 2021 Paul Lamere

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Reporting Issues

If you encounter any problems, please submit an issue along with a detailed description using the [issue tracker](<https://github.com/spotipy-dev/spotipy/issues>) on GitHub.

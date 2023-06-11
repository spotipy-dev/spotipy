# Spotipy

##### A light weight Python library for the Spotify Web API. 

Spotipy was created to allow a user to easily handle any data that can be supplied by the Spotify API. This includes anything from adding a song to your queue, viewing a playlist, or following another user (and much, much more). With Spotipy you get full access to all of the music data provided by the Spotify platform. This includes access to all endpoints and support for user authorization. For details on the capabilities you are encouraged to review the [Spotify Web API](https://developer.spotify.com/documentation/web-api) documentation.

Spotipy uses the MIT License, which allows free use of the software and zero liability toward the creators of the code. 

![Tests](https://github.com/plamere/spotipy/workflows/Tests/badge.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Contributing](#contributing)
- [License](#license)
- [Documentation](#documentation)
- [FAQ](#frequently-asked-questions)
- [Reporting Issues/Other Questions](#reporting-issues)


## Code of Conduct

Here at Spotipy, we promote an environment which is open and welcoming to all. As contributors and maintainers we want to guarantee an experience which is free of harassment for everyone.

Please be sure to read the full [Code of Conduct](code_of_conduct.md) and follow these guidelines at all times when interacting with Spotipy and its users.  


## Installation

```bash
pip install spotipy
```

alternatively, for Windows users 

```bash
py -m pip install spotipy
```

or upgrade

```bash
pip install spotipy --upgrade
```

## Quick Start

A full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples).

To get started, install spotipy and create an app on https://developers.spotify.com/.
Add your new ID and SECRET to your environment:

### Without user authentication

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])
```

### With user authentication

A redirect URI must be added to your application at [My Dashboard](https://developer.spotify.com/dashboard/applications) to access user authenticated features.

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope="user-library-read"))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
```

## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).


## Frequently Asked Questions

For common questions please check our [FAQ](FAQ.md).


## Reporting Issues

You can ask questions about Spotipy on
[Stack Overflow](http://stackoverflow.com/questions/ask).
Don’t forget to add the *Spotipy* tag, and any other relevant tags as well, before posting.

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/plamere/spotipy/issues).
Or just send a pull request.

## License

Spotipy is licensed under the MIT License. You can view more here: [LICENSE.md](LICENSE.md)

# Spotipy

##### Spotipy is a lightweight Python library for the [Spotify Web API](https://developer.spotify.com/documentation/web-api). With Spotipy you get full access to all of the music data provided by the Spotify platform.

![Integration tests](https://github.com/spotipy-dev/spotipy/actions/workflows/integration_tests.yml/badge.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=master)](https://spotipy.readthedocs.io/en/latest/?badge=master) [![Discord server](https://img.shields.io/discord/1244611850700849183?style=flat&logo=discord&logoColor=7289DA&color=7289DA)](https://discord.gg/HP6xcPsTPJ)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Reporting Issues](#reporting-issues)
- [Contributing](#contributing)

## Features

Spotipy supports all of the features of the Spotify Web API including access to all end points, and support for user authorization. For details on the capabilities you are encouraged to review the [Spotify Web API](https://developer.spotify.com/web-api/) documentation.

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

To get started, [install spotipy](#installation), create a new account or log in on https://developers.spotify.com/. Go to the [dashboard](https://developer.spotify.com/dashboard), create an app and add your new ID and SECRET (ID and SECRET can be found on an app setting) to your environment ([step-by-step video](https://www.youtube.com/watch?v=kaBVN8uP358)):

### Example without user authentication

```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])
```
Expected result:
```
0 Island In The Sun
1 Say It Ain't So
2 Buddy Holly
.
.
.
18 Troublemaker
19 Feels Like Summer
```


### Example with user authentication

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
Expected result will be the list of music that you liked. For example if you liked Red and Sunflower, the result will be:
```
0 Post Malone  –  Sunflower - Spider-Man: Into the Spider-Verse
1 Taylor Swift  –  Red
```


## Reporting Issues

For common questions please check our [FAQ](FAQ.md).

You can ask questions about Spotipy on
[Stack Overflow](http://stackoverflow.com/questions/ask).
Don’t forget to add the *Spotipy* tag, and any other relevant tags as well, before posting.

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/plamere/spotipy/issues).
Or just send a pull request.

## Contributing

If you are a developer with Python experience, and you would like to contribute to Spotipy, please be sure to follow the guidelines listed on documentation page

> #### [Visit the guideline](https://spotipy.readthedocs.io/en/#contribute)

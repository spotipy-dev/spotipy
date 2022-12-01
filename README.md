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

## Reporting Issues

For common questions please check our [FAQ](FAQ.md).

You can ask questions about Spotipy on
[Stack Overflow](http://stackoverflow.com/questions/ask).
Don’t forget to add the *Spotipy* tag, and any other relevant tags as well, before posting.

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/plamere/spotipy/issues).
Or just send a pull request. 

Refer to Documentation below for collecting information for bug reporting.

## Bud Reporting

### Describing the Bug 

Try to explain in detail what the bug is and how it is caused.

### Posting your code

Try to have the code either well commented or in a clean code style that is easy to follow and clear for the person debugging the issue to walk themselves through the code.

### Expected behavior

Explain what behavior you are looking for in the code and the expected output. 

### Output

Paste and format the output of your code. This includes errors (with complete stacktraces), logs and any on the fly debugging (print statements etc...)

Please REMOVE any sensitive information from your bug report. 

### Environment

This section is collecting information about your system and environment which will include:
 -OS: [e.g., Windows, Mac]
 -Python version [e.g., 3.7.0]
 -spotipy version [e.g., 2.12.0]
 -your IDE (if using any) [e.g., PyCharm, Jupyter Notebook IDE, Google Colab]

### Additional context

This section is very important to speed up the process of bug fixing. Add any additional comments or context that can help everyone find and reproduce your bug. 

This can include an explanation of what you are doing and walking through pseudocode, explain what you think cause the issue and if you have experience writing libraries explaining where you think the bug is coming from and where to look.

The point of this context section is to narrow down the issue to the best of your ability so that other contributors can help track the bug down.

# Spotipy

##### A light weight Python library for the Spotify Web API

![Tests](https://github.com/plamere/spotipy/workflows/Tests/badge.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/spotipy/badge/?version=latest)](https://spotipy.readthedocs.io/en/latest/?badge=latest)

## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).

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
These examples will only run with the **user authentication** option. Most Spotipy functions require user authentication to 
function as expected.

To get started, install spotipy and create an app on https://developers.spotify.com/.
* After you have created your application, you will need to add a redirect URI in your application settings. You can use http://localhost
* From your app settings, retreive the URI you created, Client ID and Client secret
* You will need to add these secrets to your `.zshrc` or `.bash_profile` depending on what environment your terminal shell is in

```
# spotipy credentials
export SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
export SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
export SPOTIPY_REDIRECT_URI='http://localhost' # or whatever you chose to use here
```

### Without user authentication (this will not work with many of Python files in the example directory)

```
python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_APP_CLIENT_ID",
                                                           client_secret="YOUR_APP_CLIENT_SECRET"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])
```

### With user authentication (preferred method)

A redirect URI must be added to your application at [My Dashboard](https://developer.spotify.com/dashboard/applications) to access user authenticated features.

```
python
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

* To test that you have completed the setup successfully, run [my_top_artists.py](https://github.com/spotipy-dev/spotipy/blob/master/examples/my_top_artists.py)
* When you run the script (`python3 my_top_artists.py`) you may see the following prompt
```
Using `localhost` as redirect URI without a port. Specify a port (e.g. `localhost:8080`) to allow automatic retrieval of authentication code instead of having to copy and paste the URL your browser is redirected to.
Enter the URL you were redirected to:
```
* A webpage should open on your device. Copy and paste the URL for that webpage and enter it in the prompt
* After entering the URL, the script should return your top artists if everything has been setup correctly

## Reporting Issues

For common questions please check our [FAQ](FAQ.md).

You can ask questions about Spotipy on
[Stack Overflow](http://stackoverflow.com/questions/ask).
Don’t forget to add the *Spotipy* tag, and any other relevant tags as well, before posting.

If you have suggestions, bugs or other issues specific to this library,
file them [here](https://github.com/plamere/spotipy/issues).
Or just send a pull request.

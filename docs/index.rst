.. image:: images/spotify-web-api-doc.jpg
   :width: 100 %

Welcome to Spotipy!
===================================

*Spotipy* is a lightweight Python library for the `Spotify Web API
<https://developer.spotify.com/documentation/web-api/>`_. With *Spotipy*
you get full access to all of the music data provided by the Spotify platform.

Assuming you set the ``SPOTIPY_CLIENT_ID`` and ``SPOTIPY_CLIENT_SECRET``
environment variables (here is a `video <https://youtu.be/kaBVN8uP358>`_ explaining how to do so). For a longer tutorial with examples included, refer to this `video playlist <https://www.youtube.com/watch?v=tmt5SdvTqUI&list=PLqgOPibB_QnzzcaOFYmY2cQjs35y0is9N&index=1>`_. Below is a quick example of using *Spotipy* to list the
names of all the albums released by the artist 'Birdy'::

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

Here's another example showing how to get 30 second samples and cover art
for the top 10 tracks for Led Zeppelin::

    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.artist_top_tracks(lz_uri)

    for track in results['tracks'][:10]:
        print('track    : ' + track['name'])
        print('audio    : ' + track['preview_url'])
        print('cover art: ' + track['album']['images'][0]['url'])
        print()

Finally, here's an example that will get the URL for an artist image given the
artist's name::

    import spotipy
    import sys
    from spotipy.oauth2 import SpotifyClientCredentials

    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    if len(sys.argv) > 1:
        name = ' '.join(sys.argv[1:])
    else:
        name = 'Radiohead'

    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        print(artist['name'], artist['images'][0]['url'])


Features
========

*Spotipy* supports all of the features of the Spotify Web API including access
to all end points, and support for user authorization. For details on the
capabilities you are encouraged to review the `Spotify Web
API <https://developer.spotify.com/documentation/web-api/>`_ documentation.

Installation
============

**Installing Spotipy on Windows**:

- Install Python: Download and install Python from the official Python website (https://www.python.org/downloads/).

- Install Spotipy: Open a command prompt and run pip install spotipy.
Open command prompt and run the following::

   pip install spotipy

- Authenticate your app: Register your app on the Spotify Developer Dashboard and obtain a client ID and client secret.

**Installing Spotipy on macOS**:


- Install Homebrew: Install Homebrew, a package manager for macOS.

- Run the followng command::

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

- Install Python: Run brew install python in the terminal::

   brew install python

- Install Spotipy: Run pip install spotipy in the terminal::

   pip install spotipy

- Authenticate your app: Register your app on the Spotify Developer Dashboard and obtain a client ID and client secret.

**Installing Spotipy on Linux**:

- Install Python: Use your Linux distribution's package manager to install Python using the following command::

   sudo apt-get install python3

- Install pip: Use your Linux distribution's package manager to install pip using the command::

   sudo apt-get install python3-pip

- Install Spotipy: Run pip install spotipy in the terminal.

   pip install spotipy

- Authenticate your app: Register your app on the Spotify Developer Dashboard and obtain a client ID and client secret.


 .. Install or upgrade *Spotipy* with::

    pip install spotipy --upgrade

You can get the source from github at https://github.com/plamere/spotipy

Getting Started with Spotipy
===============

Before you can use Spotipy, there are a few things you need to do:

Register your app: To make authorized calls to the Spotify Web API, you need to register your app and obtain a client ID and client secret. You can register your app at My Dashboard <https://developer.spotify.com/dashboard/applications>_. Make sure to keep your client ID and client secret secure.

Choose an authorization flow: Spotipy supports two authorization flows: the Authorization Code flow and the Client Credentials flow. Choose the one that's suitable for your application.
  - **Authorization Code flow** This method is suitable for long-running applications
    which the user logs into once. It provides an access token that can be refreshed.

   .. note:: This method requires you to add a redirect URI to your application at 
              `My Dashboard <https://developer.spotify.com/dashboard/applications>`_.
              See `Redirect URI`_ for more details.

  - **The Client Credentials flow** This is suitable for short-lived applications that don't require user permission. It makes it possible to authenticate your requests to the Spotify Web API and to obtain a higher rate limit than you would with the Authorization Code flow.

Before you can use Spotipy's methods, you need to authorize your app by registering it at My Dashboard <https://developer.spotify.com/dashboard/applications>_. This will give you a *client id* and *client secret* that you'll need to use in your code.


Authorization Code Flow
=======================

This flow is suitable for long-running applications in which the user grants
permission only once. It provides an access token that can be refreshed.
Since the token exchange involves sending your secret key, perform this on a
secure location, like a backend service, and not from a client such as a
browser or from a mobile app.

Quick start
-----------

To support the **Client Authorization Code Flow** *Spotipy* provides a
class SpotifyOAuth that can be used to authenticate requests like so::

    import spotipy
    from spotipy.oauth2 import SpotifyOAuth

    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

or if you are reluctant to immortalize your app credentials in your source code,
you can set environment variables like so (use ``$env:"credentials"`` instead of ``export``
on Windows)::

    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

Scopes
------

See `Using
Scopes <https://developer.spotify.com/documentation/web-api/concepts/scopes/>`_ for information
about scopes.

Redirect URI
------------

The **Authorization Code Flow** needs you to add a **redirect URI**
to your application at 
`My Dashboard <https://developer.spotify.com/dashboard/applications>`_
(navigate to your application and then *[Edit Settings]*).

The ``redirect_uri`` argument or ``SPOTIPY_REDIRECT_URI`` environment variable
must match the redirect URI added to your application in your Dashboard.
The redirect URI can be any valid URI (it does not need to be accessible)
such as ``http://example.com``, ``http://localhost`` or ``http://127.0.0.1:9090``.

    .. note:: If you choose an `http`-scheme URL, and it's for `localhost` or
     `127.0.0.1`, **AND** it specifies a port, then spotipy will instantiate
      a server on the indicated response to receive the access token from the
      response at the end of the oauth flow [see the code](https://github.com/plamere/spotipy/blob/master/spotipy/oauth2.py#L483-L490).


Client Credentials Flow
=======================

The Client Credentials flow is used in server-to-server authentication. Only
endpoints that do not access user information can be accessed. The advantage here
in comparison with requests to the Web API made without an access token,
is that a higher rate limit is applied.

As opposed to the Authorization Code Flow, you will not need to set ``SPOTIPY_REDIRECT_URI``,
which means you will never be redirected to the sign in page in your browser::

    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'

To support the **Client Credentials Flow** *Spotipy* provides a
class SpotifyClientCredentials that can be used to authenticate requests like so::


    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlists = sp.user_playlists('spotify')
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None


IDs URIs and URLs
=================

*Spotipy* supports a number of different ID types:

  - **Spotify URI** - The resource identifier that you can enter, for example, in
    the Spotify Desktop client's search box to locate an artist, album, or
    track. Example: ``spotify:track:6rqhFgbbKwnb9MLmUQDhG6``
  - **Spotify URL** - An HTML link that opens a track, album, app, playlist or other
    Spotify resource in a Spotify client. Example:
    ``http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6``
  - **Spotify ID** - A base-62 number that you can find at the end of the Spotify
    URI (see above) for an artist, track, album, etc. Example:
    ``6rqhFgbbKwnb9MLmUQDhG6``

In general, any *Spotipy* method that needs an artist, album, track or playlist ID
will accept ids in any of the above form


Customized token caching
========================

Tokens are refreshed automatically and stored by default in the project main folder.
As this might not suit everyone's needs, spotipy provides a way to create customized
cache handlers.

https://github.com/plamere/spotipy/blob/master/spotipy/cache_handler.py

The custom cache handler would need to be a class that inherits from the base
cache handler ``CacheHandler``. The default cache handler ``CacheFileHandler`` is a good example.
An instance of that new class can then be passed as a parameter when
creating ``SpotifyOAuth``, ``SpotifyPKCE`` or ``SpotifyImplicitGrant``.
The following handlers are available and defined in the URL above.
  - ``CacheFileHandler``
  - ``MemoryCacheHandler``
  - ``DjangoSessionCacheHandler``
  - ``FlaskSessionCacheHandler``
  - ``RedisCacheHandler``

Feel free to contribute new cache handlers to the repo.

Examples
=======================

There are many more examples of how to use *Spotipy* in the `Examples
Directory <https://github.com/plamere/spotipy/tree/master/examples>`_ on Github

API Reference
==============

:mod:`client` Module
=======================

.. automodule:: spotipy.client
    :members:
    :undoc-members:
    :special-members: __init__
    :show-inheritance:

:mod:`oauth2` Module
=======================

.. automodule:: spotipy.oauth2
    :members:
    :undoc-members:
    :special-members: __init__
    :show-inheritance:

:mod:`util` Module
--------------------

.. automodule:: spotipy.util
    :members:
    :undoc-members:
    :special-members: __init__
    :show-inheritance:


Support
=======
You can ask questions about Spotipy on Stack Overflow.   Don’t forget to add the
*Spotipy* tag, and any other relevant tags as well, before posting.

    http://stackoverflow.com/questions/ask

If you think you've found a bug, let us know at
`Spotify Issues <https://github.com/plamere/spotipy/issues>`_


Troubleshooting
=======

This section aims to address common issues that users may encounter while working with Spotipy and provide practical solutions to resolve them.

**Authentication errors**: Make sure that you have correctly set up your credentials and are using the correct authorization flow to avoid authenthication erros. Ensure that your client ID and client secret are correct and that you have added the appropriate redirect URIs to your Spotify Developer Dashboard.

**Playlist creation errors**: If you're having trouble creating a playlist, check that your user ID is correct, and that the user has the necessary permissions to create playlists. Additionally, make sure that your code is formatted correctly, along with the fact that you are sending the appropriate request to the Spotify API.

**Search errors**: If you're having problems when searching for music, make sure that you are providing the correct search query parameters. You should also check the Spotify API documentation to ensure that the endpoint you're using supports the search parameters you are providing.

**API changes**: Sometimes the Spotify API may change, causing errors in your application. To fix this, check the Spotify API documentation to see if there are any changes that may affect your code and update it accordingly.

**Rate limiting**: Making too many requests to the Spotify API within a short period of time, will result in you hitting the rate limit. To prevent this, use caching and backoff mechanisms in your code

**Authorization errors**: If you encounter authorization errors, make sure that you have correctly set up your credentials and are using the correct authorization flow. You may also need to check if your access token has expired and obtain a new one if necessary.

Contribute
==========

Spotipy authored by Paul Lamere (plamere) with contributions by:

  - Daniel Beaudry (`danbeaudry on Github <https://github.com/danbeaudry>`_)
  - Faruk Emre Sahin (`fsahin on Github <https://github.com/fsahin>`_)
  - George (`rogueleaderr on Github <https://github.com/rogueleaderr>`_)
  - Henry Greville (`sethaurus on Github <https://github.com/sethaurus>`_)
  - Hugo van Kemanade (`hugovk on Github <https://github.com/hugovk>`_)
  - José Manuel Pérez (`JMPerez on Github <https://github.com/JMPerez>`_)
  - Lucas Nunno (`lnunno on Github <https://github.com/lnunno>`_)
  - Lynn Root (`econchick on Github <https://github.com/econchick>`_)
  - Matt Dennewitz (`mattdennewitz on Github <https://github.com/mattdennewitz>`_)
  - Matthew Duck (`mattduck on Github <https://github.com/mattduck>`_)
  - Michael Thelin (`thelinmichael on Github <https://github.com/thelinmichael>`_)
  - Ryan Choi (`ryankicks on Github <https://github.com/ryankicks>`_)
  - Simon Metson (`drsm79 on Github <https://github.com/drsm79>`_)
  - Steve Winton (`swinton on Github <https://github.com/swinton>`_)
  - Tim Balzer (`timbalzer on Github <https://github.com/timbalzer>`_)
  - `corycorycory on Github <https://github.com/corycorycory>`_
  - Nathan Coleman (`nathancoleman on Github <https://github.com/nathancoleman>`_) 
  - Michael Birtwell (`mbirtwell on Github <https://github.com/mbirtwell>`_)
  - Harrison Hayes (`Harrison97 on Github <https://github.com/Harrison97>`_)
  - Stephane Bruckert (`stephanebruckert on Github <https://github.com/stephanebruckert>`_)
  - Ritiek Malhotra (`ritiek on Github <https://github.com/ritiek>`_)

If you are a developer with Python experience, and you would like to contribute to Spotipy, please
be sure to follow the guidelines listed below:

Export the needed Environment variables:::
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_CLIENT_USERNAME=client_username_here # This is actually an id not spotify display name
    export SPOTIPY_REDIRECT_URI=http://localhost:8080 # Make url is set in app you created to get your ID and SECRET

Create virtual environment, install dependencies, run tests:::
    $ virtualenv --python=python3.7 env
    (env) $ pip install --user -e .
    (env) $ python -m unittest discover -v tests

**Lint**

To automatically fix the code style:::
    pip install autopep8
    autopep8 --in-place --aggressive --recursive .

To verify the code style:::
    pip install flake8
    flake8 .

To make sure if the import lists are stored correctly:::
    pip install isort
    isort . -c -v

**Publishing (by maintainer)**

- Bump version in setup.py
- Bump and date changelog
- Add to changelog:
::
    ## Unreleased

    // Add your changes here and then delete this line
- Commit changes
- Package to pypi:
::
    python setup.py sdist bdist_wheel
    python3 setup.py sdist bdist_wheel
    twine check dist/*
    twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing dist/*.(whl|gz|zip)~dist/*linux*.whl
- Create github release https://github.com/plamere/spotipy/releases with the changelog content for the version and a short name that describes the main addition
- Build the documentation again to ensure it's on the latest version

**Changelog**

Don't forget to add a short description of your change in the `CHANGELOG <https://github.com/plamere/spotipy/blob/master/CHANGELOG.md>`_!



License
=======
(Taken from https://github.com/plamere/spotipy/blob/master/LICENSE.md)::

    MIT License
    Copyright (c) 2021 Paul Lamere
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
    (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, 
    publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do
    so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR 
    IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


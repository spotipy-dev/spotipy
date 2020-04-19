.. image:: images/spotify-web-api-doc.jpg
   :width: 100 %

Welcome to Spotipy!
===================================
*Spotipy* is a lightweight Python library for the `Spotify Web API
<https://developer.spotify.com/web-api/>`_. With *Spotipy*
you get full access to all of the music data provided by the Spotify platform.

Assuming you set the ``SPOTIPY_CLIENT_ID`` and ``SPOTIPY_CLIENT_SECRET``
environment variables, here's a quick example of using *Spotipy* to list the
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

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

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
API <https://developer.spotify.com/web-api/>`_ documentation.

Installation
============

Install or upgrade *Spotipy* with::

    pip install spotipy --upgrade

Or you can get the source from github at https://github.com/plamere/spotipy

Getting Started
===============

All methods require user authorization. You will need to register your app at 
`My Dashboard <https://developer.spotify.com/dashboard/applications>`_ 
to get the credentials necessary to make authorized calls
(a *client id* and *client secret*).

*Spotipy* supports two authorization flows:

  - The **Authorization Code flow** This method is suitable for long-running applications
    which the user logs into once. It provides an access token that can be refreshed.

    .. note:: Requires you to add a redirect URI to your application at 
              `My Dashboard <https://developer.spotify.com/dashboard/applications>`_.
              See `Redirect URI`_ for more details.

  - The **Client Credentials flow**  The method makes it possible
    to authenticate your requests to the Spotify Web API and to obtain
    a higher rate limit than you would with the Authorization Code flow.


Authorization Code Flow
=======================

This flow is suitable for long-running applications in which the user grants
permission only once. It provides an access token that can be refreshed.
Since the token exchange involves sending your secret key, perform this on a
secure location, like a backend service, and not from a client such as a
browser or from a mobile app.

To support the **Authorization Code Flow** *Spotipy* provides a
utility method ``util.prompt_for_user_token`` that will attempt to authorize the
user. You can pass your app credentials directly into the method as arguments::

    util.prompt_for_user_token(username,
                               scope,
                               client_id='your-spotify-client-id',
                               client_secret='your-spotify-client-secret',
                               redirect_uri='your-app-redirect-url')

or if you are reluctant to immortalize your app credentials in your source code,
you can set environment variables like so (use ``SET`` instead of ``export``
on Windows)::

    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

Call the ``util.prompt_for_user_token`` method with the username, the
desired scope (see `Using
Scopes <https://developer.spotify.com/web-api/using-scopes/>`_ for information
about scopes) and credentials (passed directly or via environment variables)
to start the authorization process. 

Redirect URI
------------
For the **Authorization Code Flow** you need to add a **redirect URI**
to your application at 
`My Dashboard <https://developer.spotify.com/dashboard/applications>`_
(navigate to your application and then *[Edit Settings]*).

The ``redirect_uri`` argument or ``SPOTIPY_REDIRECT_URI`` environment variable
must match the redirect URI added to your application in your Dashboard.
The redirect URI can be any valid URI (it does not need to be accessible)
such as ``http://example.com``, ``http://localhost`` or ``http://127.0.0.1:9090``. 

Calling ``util.prompt_for_user_token`` will open Spotify's 
application authorization page in your browser (and require you to log in
if you are not already logged in to spotify.com), unless a locally cached
access token exist from a previous authorization/authentication.

After successful authentication your browser will be redirected to
the redirect URI of your application, e.g. ``http://localhost:9090/?code=<code>``.

If your request URI is set to ``http://127.0.0.1:<port>`` or ``http://localhost:<port>``
Spotipy will automatically complete the authorization process 
(obtain the ``<code>`` from the URI).

If your request URI is set to any other URI you will need to manually copy the 
URI from the browser's address bar and paste it into the terminal/console where
your Spotipy script is running (Spotipy will instruct you to do so).

Example
-------

Here's an example of getting user authorization to read a user's saved tracks::

    import sys
    import spotipy
    import spotipy.util as util

    scope = 'user-library-read'

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_saved_tracks()
        for item in results['items']:
            track = item['track']
            print(track['name'] + ' - ' + track['artists'][0]['name'])
    else:
        print("Can't get token for", username)

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

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlists = sp.user_playlists('spotify')
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None


IDs URIs and URLs
=======================
*Spotipy* supports a number of different ID types:

  - Spotify URI - The resource identifier that you can enter, for example, in
    the Spotify Desktop client's search box to locate an artist, album, or
    track. Example: spotify:track:6rqhFgbbKwnb9MLmUQDhG6
  - Spotify URL - An HTML link that opens a track, album, app, playlist or other
    Spotify resource in a Spotify client. Example:
    http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6
  - Spotify ID - A base-62 number that you can find at the end of the Spotify
    URI (see above) for an artist, track, album, etc. Example:
    6rqhFgbbKwnb9MLmUQDhG6

In general, any *Spotipy* method that needs an artist, album, track or playlist ID
will accept ids in any of the above form

Examples
========
Here are a few more examples of using *Spotipy*, this time using the Authorization Code Flow
to access your personal Spotify account data.

Add tracks to a playlist::

    import sys

    import spotipy
    import spotipy.util as util

    if len(sys.argv) > 3:
        username = sys.argv[1]
        playlist_id = sys.argv[2]
        track_ids = sys.argv[3:]
    else:
        print("Usage: %s username playlist_id track_id ..." % (sys.argv[0],))
        sys.exit()

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        print(results)
    else:
        print("Can't get token for", username)


Shows the contents of every playlist owned by a user::

    # shows a user's playlists (need to be authenticated via oauth)

    import sys
    import spotipy
    import spotipy.util as util

    def show_tracks(tracks):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
                track['name']))


    if __name__ == '__main__':
        if len(sys.argv) > 1:
            username = sys.argv[1]
        else:
            print("Whoops, need your username!")
            print("usage: python user_playlists.py [username]")
            sys.exit()

        token = util.prompt_for_user_token(username)

        if token:
            sp = spotipy.Spotify(auth=token)
            playlists = sp.user_playlists(username)
            for playlist in playlists['items']:
                if playlist['owner']['id'] == username:
                    print()
                    print(playlist['name'])
                    print ('  total tracks', playlist['tracks']['total'])
                    results = sp.playlist(playlist['id'],
                        fields="tracks,next")
                    tracks = results['tracks']
                    show_tracks(tracks)
                    while tracks['next']:
                        tracks = sp.next(tracks)
                        show_tracks(tracks)
        else:
            print("Can't get token for", username)


More Examples
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


Contribute
==========
Spotipy authored by Paul Lamere (plamere) with contributions by:

  - Daniel Beaudry // danbeaudry
  - Faruk Emre Sahin // fsahin
  - George // rogueleaderr
  - Henry Greville // sethaurus
  - Hugo // hugovk
  - José Manuel Pérez // JMPerez
  - Lucas Nunno // lnunno
  - Lynn Root // econchick
  - Matt Dennewitz // mattdennewitz
  - Matthew Duck // mattduck
  - Michael Thelin // thelinmichael
  - Ryan Choi // ryankicks
  - Simon Metson // drsm79
  - Steve Winton // swinton
  - Tim Balzer // timbalzer
  - corycorycory // corycorycory
  - Nathan Coleman // nathancoleman
  - Michael Birtwell // mbirtwell
  - Harrison Hayes // Harrison97
  - Stephane Bruckert // stephanebruckert
  - Ritiek Malhotra // ritiek

License
=======
https://github.com/plamere/spotipy/blob/master/LICENSE.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


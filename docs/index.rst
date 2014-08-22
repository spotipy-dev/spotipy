Spotipy
===================================
Spotipy is a lightweight Python library for the `Spotify Web API
<https://developer.spotify.com/web-api/>`_. With *spotipy*
you get full access to all of the music data provided by the Spotify platform. 

Here's a quick example of using *spotipy* to list the names of all the albums
released by the artist 'Birdy'::

    import spotipy

    birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
    spotify = spotipy.Spotify()

    results = spotify.artist_albums(birdy_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = spotify.next(results)
        albums.extend(results['items'])

    for album in albums:
        print(album['name'])
        print album

Here's another example showing how to get 30 second samples and cover art
for the top 10 tracks for Led Zeppelin::

    import spotipy

    lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

    spotify = spotipy.Spotify()
    results = spotify.artist_top_tracks(lz_uri)

    for track in results['tracks'][:10]:
        print 'track    : ' + track['name']
        print 'audio    : ' + track['preview_url']
        print 'cover art: ' + track['album']['images'][0]['url']
        print

Finally, here's an example that will get the URL for an artist image given the
artist's name::

    import spotipy
    import sys

    spotify = spotipy.Spotify()

    if len(sys.argv) > 1:
        name = ' '.join(sys.argv[1:])
    else:
        name = 'Radiohead'

    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        print artist['name'], artist['images'][0]['url']


Features
========
*Spotipy* supports all of the features of the Spotify Web API including access
to all end points, and support for user authorization.

Installation
============
Install spotipy with::

    pip install SpotifyWebAPI

Or with::

    easy_install SpotifyWebAPI

Or you can get the source from github at https://github.com/plamere/spotipy

Getting Started
===============

To use *spotipy* import the spotipy package, and create a Spotify object.  For
methods that require authorization, pass the authorization token into the
Spotify constructor

Non authorized requests::

    import spotipy
    spotify = spotipy.Spotify()
    results = spotify.search(q='artist:' + name, type='artist')
    print results

Authorization
-------------
Many methods require user authentication. For these requests you will need to
generate an authorization token that indicates that the user has granted
permission for your application to perform the given task. Spotipy provides a
utility method ``util.prompt_for_user_token`` that will attempt to authorize the
user.  You can pass your app credentials directly into the method as arguments,
or if you are reluctant to immortalize your app credentials in your source code, 
you can set environment variables like so::

    export CLIENT_ID='your-spotify-client-id'
    export CLIENT_SECRET='your-spotify-client-secret'
    export REDIRECT_URI='your-app-redirect-url'

Call ``util.prompt_for_user_token`` method with the username and the 
desired scope (see `Using
Scopes <https://developer.spotify.com/web-api/using-scopes/>`_ for information
about scopes) and credentials. This will coordinate the user authorization via
a the browser.  The credentials are cached locally 


Authorized requests::

    import sys
    import spotipy
    import spotipy.util as util

    scope = 'user-library-read'

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Usage: %s username" % (sys.argv[0],)
        sys.exit()

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_saved_tracks()
        for item in results['items']:
            track = item['track']
            print track['name'] + ' - ' + track['artists'][0]['name']
    else:
        print "Can't get token for", username


spotipy Package
===============

:mod:`spotipy` Package
----------------------

.. automodule:: spotipy.__init__
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`client` Module
--------------------

.. automodule:: spotipy.client
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`oauth2` Module
--------------------

.. automodule:: spotipy.oauth2
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`util` Module
------------------

.. automodule:: spotipy.util
    :members:
    :undoc-members:
    :show-inheritance:


Support
=======

Contribute
==========

License
=======


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


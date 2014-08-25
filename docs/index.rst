.. image:: images/spotify-web-api-doc.jpg
   :width: 100 %

Welcome to Spotipy!
===================================
*Spotipy* is a lightweight Python library for the `Spotify Web API
<https://developer.spotify.com/web-api/>`_. With *Spotipy*
you get full access to all of the music data provided by the Spotify platform. 

Here's a quick example of using *Spotipy* to list the names of all the albums
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
to all end points, and support for user authorization. For details on the
capabilities you are encouraged to review the `Spotify Web
API <https://developer.spotify.com/web-api/>`_ documentation.

Installation
============
Install *Spotipy* with::

    pip install spotipy

Or with::

    easy_install spotipy

Or you can get the source from github at https://github.com/plamere/spotipy

Getting Started
===============

Non-Authorized requests
=======================
For methods that do not require authorization, simply create a Spotify object
and start making method calls like so::

    import spotipy
    spotify = spotipy.Spotify()
    results = spotify.search(q='artist:' + name, type='artist')
    print results

Authorized requests
=======================
Many methods require user authentication. For these requests you will need to
generate an authorization token that indicates that the user has granted
permission for your application to perform the given task.  You will need to
register your app to get the credentials necessary to make authorized calls.
Register your app at 
`My Applications
<https://developer.spotify.com/my-applications/#!/applications>`_.


*Spotipy* provides a
utility method ``util.prompt_for_user_token`` that will attempt to authorize the
user.  You can pass your app credentials directly into the method as arguments,
or if you are reluctant to immortalize your app credentials in your source code, 
you can set environment variables like so::

    export SPOTIPY_CLIENT_ID='your-spotify-client-id'
    export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
    export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

Call ``util.prompt_for_user_token`` method with the username and the 
desired scope (see `Using
Scopes <https://developer.spotify.com/web-api/using-scopes/>`_ for information
about scopes) and credentials. This will coordinate the user authorization via
your web browser.  The credentials are cached locally and are used to automatically
re-authorized expired tokens.

Here's an example of getting user authorization to read a user's saved tracks::

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
Here are a few more examples of using *Spotipy*.

Add tracks to a playlist::

    import pprint
    import sys

    import spotipy
    import spotipy.util as util

    if len(sys.argv) > 3:
        username = sys.argv[1]
        playlist_id = sys.argv[2]
        track_ids = sys.argv[3:]
    else:
        print "Usage: %s username playlist_id track_id ..." % (sys.argv[0],)
        sys.exit()

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
        print results
    else:
        print "Can't get token for", username


Shows the contents of every playlist owned by a user::

    # shows a user's playlists (need to be authenticated via oauth)

    import sys
    import spotipy
    import spotipy.util as util

    def show_tracks(results):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            print "   %d %32.32s %s" % (i, track['artists'][0]['name'], 
                track['name'])


    if __name__ == '__main__':
        if len(sys.argv) > 1:
            username = sys.argv[1]
        else:
            print "Whoops, need your username!"
            print "usage: python user_playlists.py [username]"
            sys.exit()

        token = util.prompt_for_user_token(username)

        if token:
            sp = spotipy.Spotify(auth=token)
            playlists = sp.user_playlists(username)
            for playlist in playlists['items']:
                if playlist['owner']['id'] == username:
                    print
                    print playlist['name']
                    print '  total tracks', playlist['tracks']['total']
                    results = sp.user_playlist(username, playlist['id'], 
                        fields="tracks,next")
                    tracks = results['tracks']
                    show_tracks(tracks)
                    while tracks['next']:
                        tracks = sp.next(tracks)
                        show_tracks(tracks)
        else:
            print "Can't get token for", username


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
    :show-inheritance:

:mod:`oauth2` Module
=======================

.. automodule:: spotipy.oauth2
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`util` Module
--------------------

.. automodule:: spotipy.util
    :members:
    :undoc-members:
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
  - Tim Balzer // timbalzer 
  - corycorycory // corycorycory 

License
=======
https://github.com/plamere/spotipy/blob/master/LICENSE.txt


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


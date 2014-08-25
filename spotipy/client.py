# coding: utf-8

from __future__ import print_function

import sys
import base64
import requests
import json

''' A simple and thin Python library for the Spotify Web API
'''

class SpotifyException(Exception):
    def __init__(self, http_status, code, msg):
        self.http_status = http_status
        self.code = code
        self.msg = msg

    def __str__(self):
        return u'http status: {0}, code:{1} - {2}'.format(
            self.http_status, self.code, self.msg)

class Spotify(object):
    '''
        Example usage::

            import spotipy

            urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
            sp = spotipy.Spotify()

            sp.trace = True # turn on tracing

            artist = sp.artist(urn)
            print(artist)

            user = sp.user('plamere')
            print(user)
    '''

    trace = False 
    """enable tracing"""

    _auth = None
    
    def __init__(self, auth=None):
        '''
           creates a spotify object

           Parameters:
                - auth - the optional authorization token 
        '''
        self.prefix = 'https://api.spotify.com/v1/'
        self._auth = auth
        self.version = 'Spotipy version 1.320'

    def _auth_headers(self):
        if self._auth:
            return {'Authorization': 'Bearer {0}'.format(self._auth)}
        else:
            return {}

    def _internal_call(self, method, url, payload, params):
        args = dict(params=params)
        if not url.startswith('http'):
            url = self.prefix + url
        headers = self._auth_headers()
        headers['Content-Type'] = 'application/json'

        if payload:
            r = requests.request(method, url, headers=headers, 
                data=json.dumps(payload), **args)
        else:
            r = requests.request(method, url, headers=headers, **args)

        if self.trace:
            print()
            print(method, r.url)
            if payload:
                print("DATA", json.dumps(payload))

        try:
            r.raise_for_status()
        except:
            raise SpotifyException(r.status_code, 
                -1, u'%s:\n %s' % (r.url, r.json()['error']['message']))
        if len(r.text) > 0:
            results = r.json()
            if self.trace:
                print('RESP', results)
                print()
            return results
        else:
            return None

    def _get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('GET', url, payload, kwargs)

    def _post(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('POST', url, payload, kwargs)

    def _delete(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('DELETE', url, payload, kwargs)

    def _put(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('PUT', url, payload, kwargs)

    def next(self, result):
        ''' returns the next result given a paged result

            Parameters:
                - result - a previously returned paged result 
        '''
        if result['next']:
            return self._get(result['next'])
        else:
            return None

    def previous(self, result):
        ''' returns the previous result given a paged result

            Parameters:
                - result - a previously returned paged result 
        '''
        if result['previous']:
            return self._get(result['previous'])
        else:
            return None
            
    def _warn(self, msg):
        print('warning:' + msg, file=sys.stderr)

    def track(self, track_id):
        ''' returns a single track given the track's ID, URI or URL

            Parameters:
                - track_id - a spotify URI, URL or ID
        '''

        trid = self._get_id('track', track_id)
        return self._get('tracks/' + trid)

    def tracks(self, tracks):
        ''' returns a list of tracks given a list of track IDs, URIs, or URLs

            Parameters:
                - tracks - a list of spotify URIs, URLs or IDs
        '''

        tlist = [self._get_id('track', t) for t in tracks]
        return self._get('tracks/?ids=' + ','.join(tlist))

    def artist(self, artist_id):
        ''' returns a single artist given the artist's ID, URI or URL

            Parameters:
                - artist_id - an artist ID, URI or URL
        '''

        trid = self._get_id('artist', artist_id)
        return self._get('artists/' + trid)


    def artists(self, artists):
        ''' returns a list of artists given the artist IDs, URIs, or URLs

            Parameters:
                - artists - a list of  artist IDs, URIs or URLs
        '''

        tlist = [self._get_id('artist', a) for a in artists]
        return self._get('artists/?ids=' + ','.join(tlist))

    def artist_albums(self, artist_id, album_type=None, country=None, 
            limit=20, offset=0):
        ''' Get Spotify catalog information about an artist's albums

            Parameters:
                - artist_id - the artist ID, URI or URL
                - album_type - 'album', 'single', 'appears_on', 'compilation'
                - country - limit the response to one particular country.
                - limit  - the number of albums to return
                - offset - the index of the first album to return
        '''

        trid = self._get_id('artist', artist_id)
        return self._get('artists/' + trid + '/albums', album_type=album_type, 
            country=country, limit=limit, offset=offset)

    def artist_top_tracks(self, artist_id, country='US'):
        ''' Get Spotify catalog information about an artist's top 10 tracks 
            by country.

            Parameters:
                - artist_id - the artist ID, URI or URL
                - country - limit the response to one particular country.
        '''

        trid = self._get_id('artist', artist_id)
        return self._get('artists/' + trid + '/top-tracks', country=country)

    def artist_related_artists(self, artist_id):
        ''' Get Spotify catalog information about artists similar to an 
            identified artist. Similarity is based on analysis of the 
            Spotify community's listening history.

            Parameters:
                - artist_id - the artist ID, URI or URL
        '''
        trid = self._get_id('artist', artist_id)
        return self._get('artists/' + trid + '/related-artists')

    def album(self, album_id):
        ''' returns a single album given the album's ID, URIs or URL

            Parameters:
                - album_id - the album ID, URI or URL
        '''

        trid = self._get_id('album', album_id)
        return self._get('albums/' + trid)

    def album_tracks(self, album_id):
        ''' Get Spotify catalog information about an album's tracks

            Parameters:
                - album_id - the album ID, URI or URL
        '''

        trid = self._get_id('album', album_id)
        return self._get('albums/' + trid + '/tracks/')

    def albums(self, albums):
        ''' returns a list of albums given the album IDs, URIs, or URLs

            Parameters:
                - albums - a list of  album IDs, URIs or URLs
        '''

        tlist = [self._get_id('album', a) for a in albums]
        return self._get('albums/?ids=' + ','.join(tlist))

    def search(self, q, limit=10, offset=0, type='track'):
        ''' searches for an item

            Parameters:
                - q - the search query
                - limit  - the number of items to return
                - offset - the index of the first item to return
                - type - the type of item to return. One of 'artist', 'album' 
                         or 'track'
        '''
        return self._get('search', q=q, limit=limit, offset=offset, type=type)

    def user(self, user):
        ''' Gets basic profile information about a Spotify User

            Parameters:
                - user - the id of the usr
        '''
        return self._get('users/' + user)
    
    def user_playlists(self, user, limit=50, offset=0):
        ''' Gets playlists of a user

            Parameters:
                - user - the id of the usr
                - limit  - the number of items to return
                - offset - the index of the first item to return
        '''
        return self._get("users/%s/playlists" % user, limit=limit, offset=offset)

    def user_playlist(self, user, playlist_id = None, fields=None):
        ''' Gets playlist of a user

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
        '''
        if playlist_id == None:
            return self._get("users/%s/starred" % (user), fields=fields)
        plid = self._get_id('playlist', playlist_id)
        return self._get("users/%s/playlists/%s" % (user, plid), 
                    fields=fields)

    def user_playlist_create(self, user, name, public=True):
        ''' Creates a playlist for a user

            Parameters:
                - user - the id of the user
                - name - the name of the playlist
                - public - is the created playlist public
        '''
        data = {'name':name, 'public':public }
        return self._post("users/%s/playlists" % (user,), payload = data)

    def user_playlist_add_tracks(self, user, playlist_id, tracks, 
                position=None):
        ''' Adds tracks to a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - a list of track URIs, URLs or IDs
                - position - the position to add the tracks
        '''
        plid = self._get_id('playlist', playlist_id)
        ftracks = [ self._get_uri('track', tid) for tid in tracks]
        return self._post("users/%s/playlists/%s/tracks" % (user,plid), 
             payload = ftracks, position=position)

    def user_playlist_replace_tracks(self, user, playlist_id, tracks):
        ''' Replace all tracks in a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist
        '''
        plid = self._get_id('playlist', playlist_id)
        ftracks = [ self._get_uri('track', tid) for tid in tracks]
        payload = { "uris": ftracks }
        return self._put("users/%s/playlists/%s/tracks" % (user,plid), 
                payload = payload)

    def user_playlist_remove_all_occurrences_of_tracks(self, user, playlist_id, 
                        tracks):
        ''' Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist

        '''

        plid = self._get_id('playlist', playlist_id)
        ftracks = [ self._get_uri('track', tid) for tid in tracks]
        payload = { "tracks": [ {"uri": track} for track in ftracks] }
        return self._delete("users/%s/playlists/%s/tracks" % (user, plid), 
                payload = payload)

    def user_playlist_remove_specific_occurrences_of_tracks(self, user, 
            playlist_id, tracks):
        ''' Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - an array of objects containing Spotify URIs of the tracks to remove with their current positions in the playlist.  For example: 
                    [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                       { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ] 
        '''

        plid = self._get_id('playlist', playlist_id)
        ftracks = [ self._get_uri('track', tid) for tid in tracks]
        payload = { "tracks": ftracks }
        return self._delete("users/%s/playlists/%s/tracks" % (user, plid), 
                payload = payload)

    def me(self):
        ''' Get detailed profile information about the current user.
            An alias for the 'current_user' method.
        '''
        return self._get('me/')

    def current_user(self):
        ''' Get detailed profile information about the current user. 
            An alias for the 'me' method.
        '''
        return self.me()

    def current_user_saved_tracks(self, limit=20, offset=0):
        ''' Gets a list of the tracks saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of tracks to return
                - offset - the index of the first track to return

        '''
        return self._get('me/tracks', limit=limit, offset=offset)

    def current_user_saved_tracks_delete(self, tracks=[]):
        ''' Remove one or more tracks from the current user's 
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        '''
        tlist = [self._get_id('track', t) for t in tracks]
        return self._delete('me/tracks/?ids=' + ','.join(tlist))

    def current_user_saved_tracks_contains(self, tracks=[]):
        ''' Check if one or more tracks is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        '''
        tlist = [self._get_id('track', t) for t in tracks]
        return self._get('me/tracks/contains?ids=' + ','.join(tlist))


    def current_user_saved_tracks_add(self, tracks=[]):
        ''' Add one or more tracks to the current user's 
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        '''
        tlist = [self._get_id('track', t) for t in tracks]
        return self._put('me/tracks/?ids=' + ','.join(tlist))

    def _get_id(self, type, id):
        fields = id.split(':')
        if len(fields) >= 3:
            if type != fields[-2]:
                self._warn('expected id of type ' + type + ' but found type ' \
                        + fields[2] + " " + id)
            return fields[-1]
        fields = id.split('/')
        if len(fields) >= 3:
            itype = fields[-2]
            if type != itype:
                self._warn('expected id of type ' + type + ' but found type ' \
                        + itype + " " + id)
            return fields[-1]
        return id

    def _get_uri(self, type, id):
        return 'spotify:' + type + ":" + self._get_id(type, id)

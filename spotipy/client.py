# coding: utf-8


from __future__ import print_function
import sys
import base64
import requests
import json
import time

''' A simple and thin Python library for the Spotify Web API
'''

class SpotifyException(Exception):
    def __init__(self, http_status, code, msg):
        self.http_status = http_status
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'http status: {0}, code:{1} - {2}'.format(
            self.http_status, self.code, self.msg)

class Spotify(object):
    '''
        Example usage::

            import spotipy

            urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
            sp = spotipy.Spotify()

            sp.trace = True # turn on tracing
            sp.trace_out = True # turn on trace out

            artist = sp.artist(urn)
            print(artist)

            user = sp.user('plamere')
            print(user)
    '''

    trace = False  # Enable tracing?
    trace_out = False
    max_get_retries = 10

    def __init__(self, auth=None, requests_session=True,
        client_credentials_manager=None):
        '''
        Create a Spotify API object.

        :param auth: An authorization token (optional)
        :param requests_session:
            A Requests session object or a truthy value to create one.
            A falsy value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons (connection pooling).
        :param client_credentials_manager:
            SpotifyClientCredentials object

        '''
        self.prefix = 'https://api.spotify.com/v1/'
        self._auth = auth
        self.client_credentials_manager = client_credentials_manager

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                from requests import api
                self._session = api

    def _auth_headers(self):
        if self._auth:
            return {'Authorization': 'Bearer {0}'.format(self._auth)}
        elif self.client_credentials_manager:
            token = self.client_credentials_manager.get_access_token()
            return {'Authorization': 'Bearer {0}'.format(token)}
        else:
            return {}

    def _internal_call(self, method, url, payload, params):
        args = dict(params=params)
        if not url.startswith('http'):
            url = self.prefix + url
        headers = self._auth_headers()
        headers['Content-Type'] = 'application/json'

        if payload:
            args["data"] = json.dumps(payload)

        if self.trace_out:
            print(url)
        r = self._session.request(method, url, headers=headers, **args)

        if self.trace:  # pragma: no cover
            print()
            print ('headers', headers)
            print ('http status', r.status_code)
            print(method, r.url)
            if payload:
                print("DATA", json.dumps(payload))

        try:
            r.raise_for_status()
        except:
            if r.text and len(r.text) > 0 and r.text != 'null':
                raise SpotifyException(r.status_code,
                    -1, '%s:\n %s' % (r.url, r.json()['error']['message']))
            else:
                raise SpotifyException(r.status_code,
                    -1, '%s:\n %s' % (r.url, 'error'))
        finally:
            r.connection.close()
        if r.text and len(r.text) > 0 and r.text != 'null':
            results = r.json()
            if self.trace:  # pragma: no cover
                print('RESP', results)
                print()
            return results
        else:
            return None

    def _get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        retries = self.max_get_retries
        delay = 1
        while retries > 0:
            try:
                return self._internal_call('GET', url, payload, kwargs)
            except SpotifyException as e:
                retries -= 1
                status = e.http_status
                # 429 means we hit a rate limit, backoff
                if status == 429 or (status >= 500 and status < 600):
                    if retries < 0:
                        raise
                    else:
                        print ('retrying ...' + str(delay) + 'secs')
                        time.sleep(delay)
                        delay += 1
                else:
                    raise
            except Exception as e: 
                raise
                print ('exception', str(e))
                # some other exception. Requests have
                # been know to throw a BadStatusLine exception
                retries -= 1
                if retries >= 0:
                    print ('retrying ...' + str(delay) + 'secs')
                    time.sleep(delay)
                    delay += 1
                else:
                    raise


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

    def album_tracks(self, album_id, limit=50, offset=0):
        ''' Get Spotify catalog information about an album's tracks

            Parameters:
                - album_id - the album ID, URI or URL
                - limit  - the number of items to return
                - offset - the index of the first item to return
        '''

        trid = self._get_id('album', album_id)
        return self._get('albums/' + trid + '/tracks/', limit=limit, offset=offset)

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
                - type - the type of item to return. One of 'artist', 'album',
                         'track' or 'playlist'
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
        return self._get("users/%s/playlists/%s" % (user, plid), fields=fields)

    def user_playlist_tracks(self, user, playlist_id = None, fields=None,
        limit=100, offset=0):
        ''' Get full details of the tracks of a playlist owned by a user.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
        '''
        plid = self._get_id('playlist', playlist_id)
        return self._get("users/%s/playlists/%s/tracks" % (user, plid),
                    limit=limit, offset=offset, fields=fields)

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

    def user_playlist_reorder_tracks(self, user, playlist_id, range_start, insert_before,
                        range_length=1, snapshot_id=None):
        ''' Reorder tracks in a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - range_start - the position of the first track to be reordered
                - range_length - optional the number of tracks to be reordered (default: 1)
                - insert_before - the position where the tracks should be inserted
                - snapshot_id - optional playlist's snapshot ID
        '''
        plid = self._get_id('playlist', playlist_id)
        payload = { "range_start": range_start,
                    "range_length": range_length,
                    "insert_before": insert_before }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._put("users/%s/playlists/%s/tracks" % (user,plid),
                payload = payload)

    def user_playlist_remove_all_occurrences_of_tracks(self, user, playlist_id,
                        tracks, snapshot_id=None):
        ''' Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist
                - snapshot_id - optional id of the playlist snapshot

        '''

        plid = self._get_id('playlist', playlist_id)
        ftracks = [ self._get_uri('track', tid) for tid in tracks]
        payload = { "tracks": [ {"uri": track} for track in ftracks] }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete("users/%s/playlists/%s/tracks" % (user, plid),
                payload = payload)

    def user_playlist_remove_specific_occurrences_of_tracks(self, user,
            playlist_id, tracks, snapshot_id=None):
        ''' Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - an array of objects containing Spotify URIs of the tracks to remove with their current positions in the playlist.  For example:
                    [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                       { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
                - snapshot_id - optional id of the playlist snapshot
        '''

        plid = self._get_id('playlist', playlist_id)
        ftracks = []
        for tr in tracks:
            ftracks.append({
                "uri": self._get_uri("track", tr["uri"]),
                "positions": tr["positions"],
            })
        payload = { "tracks": ftracks }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
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

    def current_user_saved_albums(self, limit=20, offset=0):
        ''' Gets a list of the albums saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of albums to return
                - offset - the index of the first album to return

        '''
        return self._get('me/albums', limit=limit, offset=offset)

    def current_user_saved_tracks(self, limit=20, offset=0):
        ''' Gets a list of the tracks saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of tracks to return
                - offset - the index of the first track to return

        '''
        return self._get('me/tracks', limit=limit, offset=offset)
    
    def current_user_followed_artists(self, limit=20, after=None):
        ''' Gets a list of the artists followed by the current authorized user

            Parameters:
                - limit - the number of tracks to return
                - after - ghe last artist ID retrieved from the previous request

        '''
        return self._get('me/following', type='artist', limit=limit, after=after)

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

    def current_user_top_artists(self, limit=20, offset=0, time_range='medium_term'):
        ''' Get the current user's top artists

            Parameters:
                - limit - the number of entities to return
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed.
                  Valid-values: short_term, medium_term, long_term
        '''
        return self._get('me/top/artists', time_range=time_range, limit=limit,offset=offset)

    def current_user_top_tracks(self, limit=20, offset=0, time_range='medium_term'):
        ''' Get the current user's top tracks

            Parameters:
                - limit - the number of entities to return
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed.
                  Valid-values: short_term, medium_term, long_term
        '''
        return self._get('me/top/tracks', time_range=time_range, limit=limit,offset=offset)


    def featured_playlists(self, locale=None, country=None,
            timestamp=None, limit=20, offset = 0):
        ''' Get a list of Spotify featured playlists

            Parameters:
                - locale - The desired language, consisting of a lowercase ISO
                  639 language code and an uppercase ISO 3166-1 alpha-2 country
                  code, joined by an underscore.

                - country - An ISO 3166-1 alpha-2 country code.

                - timestamp - A timestamp in ISO 8601 format:
                  yyyy-MM-ddTHH:mm:ss. Use this parameter to specify the user's
                  local time to get results tailored for that specific date and
                  time in the day

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        '''
        return self._get('browse/featured-playlists', locale=locale,
            country=country, timestamp=timestamp, limit=limit, offset=offset)

    def new_releases(self,  country=None, limit=20, offset = 0):
        ''' Get a list of new album releases featured in Spotify

            Parameters:
                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        '''
        return self._get('browse/new-releases', country=country,
            limit=limit, offset=offset)

    def categories(self,  country=None, locale=None, limit=20, offset = 0):
        ''' Get a list of new album releases featured in Spotify

            Parameters:
                - country - An ISO 3166-1 alpha-2 country code.
                - locale - The desired language, consisting of an ISO 639
                  language code and an ISO 3166-1 alpha-2 country code, joined
                  by an underscore.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        '''
        return self._get('browse/categories', country=country, locale=locale,
            limit=limit, offset=offset)

    def category_playlists(self,  category_id=None, country=None, limit=20, offset = 0):
        ''' Get a list of new album releases featured in Spotify

            Parameters:
                - category_id - The Spotify category ID for the category.

                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        '''
        return self._get('browse/categories/' + category_id + '/playlists', country=country, 
            limit=limit, offset=offset)

    def recommendations(self, seed_artists=[], seed_genres=[], seed_tracks=[],
        limit = 20, country=None, **kwargs):
        ''' Get a list of recommended tracks for one to five seeds.

            Parameters:
                - seed_artists - a list of artist IDs, URIs or URLs

                - seed_tracks - a list of artist IDs, URIs or URLs

                - seed_genres - a list of genre names. Available genres for 
                  recommendations can be found by calling recommendation_genre_seeds

                - country - An ISO 3166-1 alpha-2 country code. If provided, all 
                  results will be playable in this country.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 100

                - min/max/target_<attribute> - For the tuneable track attributes listed 
                  in the documentation, these values provide filters and targeting on
                  results.
        '''
        params = dict(limit=limit)
        if seed_artists:
            params['seed_artists'] = [self._get_id('artist', a) for a in seed_artists]
        if seed_genres:
            params['seed_genres'] = seed_genres
        if seed_tracks:
            params['seed_tracks'] = [self._get_id('track', t) for t in seed_tracks]
        if country:
            params['market'] = country

        for attribute in ["acousticness", "danceability", "duration_ms", "energy", 
            "instrumentalness", "key", "liveness", "loudness", "mode", "popularity",
            "speechiness", "tempo", "time_signature", "valence"]:
            for prefix in ["min_", "max_", "target_"]:
                param = prefix + attribute
                if param in kwargs:
                    params[param] = kwargs[param]
        return self._get('recommendations', **params)   

    def recommendation_genre_seeds(self):
        ''' Get a list of genres available for the recommendations function. 
        '''
        return self._get('recommendations/available-genre-seeds')

    def audio_features(self, tracks=[]):
        ''' Get audio features for multiple tracks based upon their Spotify IDs
            Parameters:
                - tracks - a list of track URIs, URLs or IDs, maximum: 50 ids
        '''
        tlist = [self._get_id('track', t) for t in tracks]
        results =  self._get('audio-features?ids=' + ','.join(tlist))
        # the response has changed, look for the new style first, and if
        # its not there, fallback on the old style
        if 'audio_features' in results:
            return results['audio_features']
        else:
            return results

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

# -*- coding: utf-8 -*-

""" A simple and thin Python library for the Spotify Web API """

from __future__ import print_function

__all__ = ["Spotify", "SpotifyException"]

import json
import sys
import time

import requests
import six
import warnings


class SpotifyException(Exception):
    def __init__(self, http_status, code, msg, headers=None):
        self.http_status = http_status
        self.code = code
        self.msg = msg
        # `headers` is used to support `Retry-After` in the event of a
        # 429 status code.
        if headers is None:
            headers = {}
        self.headers = headers

    def __str__(self):
        return "http status: {0}, code:{1} - {2}".format(
            self.http_status, self.code, self.msg
        )


class Spotify(object):
    """
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
    """

    trace = False  # Enable tracing?
    trace_out = False
    max_get_retries = 10

    def __init__(
        self,
        auth=None,
        requests_session=True,
        client_credentials_manager=None,
        oauth_manager=None,
        auth_manager=None,
        proxies=None,
        requests_timeout=None,
    ):
        """
        Creates a Spotify API client.

        :param auth: An authorization token (optional)
        :param requests_session:
            A Requests session object or a truthy value to create one.
            A falsy value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons (connection pooling).
        :param client_credentials_manager:
            SpotifyClientCredentials object
        :param oauth_manager:
            SpotifyOAuth object
        :param auth_manger:
            
        :param proxies:
            Definition of proxies (optional)
        :param requests_timeout:
            Tell Requests to stop waiting for a response after a given
            number of seconds
        """
        self.prefix = "https://api.spotify.com/v1/"
        self._auth = auth
        self.client_credentials_manager = client_credentials_manager
        self.oauth_manager = oauth_manager
        self.auth_manager = auth_manager
        self.proxies = proxies
        self.requests_timeout = requests_timeout

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                from requests import api

                self._session = api

    @property
    def auth_manager(self):
        return self._auth_manager

    @auth_manager.setter
    def auth_manager(self, auth_manager):
        if auth_manager is not None:
            self._auth_manager = auth_manager
        else:
            self._auth_manager = self.client_credentials_manager or self.oauth_manager

    def _auth_headers(self):
        if self._auth:
            return {"Authorization": "Bearer {0}".format(self._auth)}
        elif self.auth_manager:
            token = self.auth_manager.get_access_token()
            return {"Authorization": "Bearer {0}".format(token)}
        else:
            return {}

    def _internal_call(self, method, url, payload, params):
        args = dict(params=params)
        args["timeout"] = self.requests_timeout
        if not url.startswith("http"):
            url = self.prefix + url
        headers = self._auth_headers()

        if "content_type" in args["params"]:
            headers["Content-Type"] = args["params"]["content_type"]
            del args["params"]["content_type"]
            if payload:
                args["data"] = payload
        else:
            headers["Content-Type"] = "application/json"
            if payload:
                args["data"] = json.dumps(payload)

        if self.trace_out:
            print(url)

        with self._session.request(
            method, url, headers=headers, proxies=self.proxies, **args
        ) as r:

            if self.trace:  # pragma: no cover
                print()
                print("Request headers:", headers)
                print("Response headers:", r.headers)
                print("HTTP status", r.status_code)
                print(method, r.url)
                if payload:
                    print("Data", json.dumps(payload))

            try:
                r.raise_for_status()
            except BaseException:
                try:
                    msg = r.json()["error"]["message"]
                except BaseException:
                    msg = "error"
                raise SpotifyException(
                    r.status_code, -1, "%s:\n %s" % (r.url, msg), headers=r.headers
                )

            try:
                results = r.json()
            except BaseException:
                results = None

        if self.trace:  # pragma: no cover
            print("Response:", results)
            print()
        return results

    def _get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        retries = self.max_get_retries
        delay = 1
        while retries > 0:
            try:
                return self._internal_call("GET", url, payload, kwargs)
            except SpotifyException as e:
                retries -= 1
                status = e.http_status
                # 429 means we hit a rate limit, backoff
                if status == 429 or (status >= 500 and status < 600):
                    if retries < 0:
                        raise
                    else:
                        sleep_seconds = int(e.headers.get("Retry-After", delay))
                        print("retrying ..." + str(sleep_seconds) + "secs")
                        time.sleep(sleep_seconds + 1)
                        delay += 1
                else:
                    raise
            except Exception as e:
                raise
                print("exception", str(e))
                # some other exception. Requests have
                # been know to throw a BadStatusLine exception
                retries -= 1
                if retries >= 0:
                    sleep_seconds = int(e.headers.get("Retry-After", delay))
                    print("retrying ..." + str(delay) + "secs")
                    time.sleep(sleep_seconds + 1)
                    delay += 1
                else:
                    raise

    def _post(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call("POST", url, payload, kwargs)

    def _delete(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call("DELETE", url, payload, kwargs)

    def _put(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call("PUT", url, payload, kwargs)

    def next(self, result):
        """ returns the next result given a paged result

            Parameters:
                - result - a previously returned paged result
        """
        if result["next"]:
            return self._get(result["next"])
        else:
            return None

    def previous(self, result):
        """ returns the previous result given a paged result

            Parameters:
                - result - a previously returned paged result
        """
        if result["previous"]:
            return self._get(result["previous"])
        else:
            return None

    def _warn_old(self, msg):
        print("warning:" + msg, file=sys.stderr)

    def _warn(self, msg, *args):
        print("warning:" + msg.format(*args), file=sys.stderr)

    def track(self, track_id):
        """ returns a single track given the track's ID, URI or URL

            Parameters:
                - track_id - a spotify URI, URL or ID
        """

        trid = self._get_id("track", track_id)
        return self._get("tracks/" + trid)

    def tracks(self, tracks, market=None):
        """ returns a list of tracks given a list of track IDs, URIs, or URLs

            Parameters:
                - tracks - a list of spotify URIs, URLs or IDs
                - market - an ISO 3166-1 alpha-2 country code.
        """

        tlist = [self._get_id("track", t) for t in tracks]
        return self._get("tracks/?ids=" + ",".join(tlist), market=market)

    def artist(self, artist_id):
        """ returns a single artist given the artist's ID, URI or URL

            Parameters:
                - artist_id - an artist ID, URI or URL
        """

        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid)

    def artists(self, artists):
        """ returns a list of artists given the artist IDs, URIs, or URLs

            Parameters:
                - artists - a list of  artist IDs, URIs or URLs
        """

        tlist = [self._get_id("artist", a) for a in artists]
        return self._get("artists/?ids=" + ",".join(tlist))

    def artist_albums(
        self, artist_id, album_type=None, country=None, limit=20, offset=0
    ):
        """ Get Spotify catalog information about an artist's albums

            Parameters:
                - artist_id - the artist ID, URI or URL
                - album_type - 'album', 'single', 'appears_on', 'compilation'
                - country - limit the response to one particular country.
                - limit  - the number of albums to return
                - offset - the index of the first album to return
        """

        trid = self._get_id("artist", artist_id)
        return self._get(
            "artists/" + trid + "/albums",
            album_type=album_type,
            country=country,
            limit=limit,
            offset=offset,
        )

    def artist_top_tracks(self, artist_id, country="US"):
        """ Get Spotify catalog information about an artist's top 10 tracks
            by country.

            Parameters:
                - artist_id - the artist ID, URI or URL
                - country - limit the response to one particular country.
        """

        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid + "/top-tracks", country=country)

    def artist_related_artists(self, artist_id):
        """ Get Spotify catalog information about artists similar to an
            identified artist. Similarity is based on analysis of the
            Spotify community's listening history.

            Parameters:
                - artist_id - the artist ID, URI or URL
        """
        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid + "/related-artists")

    def album(self, album_id):
        """ returns a single album given the album's ID, URIs or URL

            Parameters:
                - album_id - the album ID, URI or URL
        """

        trid = self._get_id("album", album_id)
        return self._get("albums/" + trid)

    def album_tracks(self, album_id, limit=50, offset=0):
        """ Get Spotify catalog information about an album's tracks

            Parameters:
                - album_id - the album ID, URI or URL
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """

        trid = self._get_id("album", album_id)
        return self._get("albums/" + trid + "/tracks/", limit=limit, offset=offset)

    def albums(self, albums):
        """ returns a list of albums given the album IDs, URIs, or URLs

            Parameters:
                - albums - a list of  album IDs, URIs or URLs
        """

        tlist = [self._get_id("album", a) for a in albums]
        return self._get("albums/?ids=" + ",".join(tlist))

    def search(self, q, limit=10, offset=0, type="track", market=None):
        """ searches for an item

            Parameters:
                - q - the search query (see how to write a query in the
                      official documentation https://developer.spotify.com/documentation/web-api/reference/search/search/)  # noqa
                - limit  - the number of items to return
                - offset - the index of the first item to return
                - type - the type of item to return. One of 'artist', 'album',
                         'track' or 'playlist'
                - market - An ISO 3166-1 alpha-2 country code or the string
                           from_token.
        """
        return self._get(
            "search", q=q, limit=limit, offset=offset, type=type, market=market
        )

    def user(self, user):
        """ Gets basic profile information about a Spotify User

            Parameters:
                - user - the id of the usr
        """
        return self._get("users/" + user)

    def current_user_playlists(self, limit=50, offset=0):
        """ Get current user playlists without required getting his profile
            Parameters:
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """
        return self._get("me/playlists", limit=limit, offset=offset)

    def playlist(self, playlist_id, fields=None, market=None):
        """ Gets playlist by id.

            Parameters:
                - playlist - the id of the playlist
                - fields - which fields to return
                - market - An ISO 3166-1 alpha-2 country code or the
                           string from_token.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get("playlists/%s" % (plid), fields=fields, market=market)

    def playlist_tracks(
        self, playlist_id, fields=None, limit=100, offset=0, market=None
    ):
        """ Get full details of the tracks of a playlist.

            Parameters:
                - playlist_id - the id of the playlist
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(
            "playlists/%s/tracks" % (plid),
            limit=limit,
            offset=offset,
            fields=fields,
            market=market,
        )

    def playlist_cover_image(self, playlist_id):
        """ Get cover of a playlist.

            Parameters:
                - playlist_id - the id of the playlist
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get("playlists/%s/images" % (plid))

    def playlist_upload_cover_image(self, playlist_id, image_b64):
        """ Replace the image used to represent a specific playlist

            Parameters:
                - playlist_id - the id of the playlist
                - image_b64 - image data as a Base64 encoded JPEG image string
                    (maximum payload size is 256 KB)
        """
        plid = self._get_id("playlist", playlist_id)
        return self._put(
            "playlists/{}/images".format(plid),
            payload=image_b64,
            content_type="image/jpeg",
        )

    def user_playlist(self, user, playlist_id=None, fields=None, market=None):
        warnings.warn(
            "You should use `playlist(playlist_id)` instead", DeprecationWarning
        )

        """ Gets playlist of a user

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
        """
        if playlist_id is None:
            return self._get("users/%s/starred" % user)
        return self.playlist(playlist_id, fields=fields, market=market)

    def user_playlist_tracks(
        self, user=None, playlist_id=None, fields=None, limit=100, offset=0, market=None
    ):
        warnings.warn(
            "You should use `playlist_tracks(playlist_id)` instead", DeprecationWarning
        )

        """ Get full details of the tracks of a playlist owned by a user.

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - fields - which fields to return
                - limit - the maximum number of tracks to return
                - offset - the index of the first track to return
                - market - an ISO 3166-1 alpha-2 country code.
        """
        return self.playlist_tracks(
            playlist_id, limit=limit, offset=offset, fields=fields, market=market
        )

    def user_playlists(self, user, limit=50, offset=0):
        """ Gets playlists of a user

            Parameters:
                - user - the id of the usr
                - limit  - the number of items to return
                - offset - the index of the first item to return
        """
        return self._get("users/%s/playlists" % user, limit=limit, offset=offset)

    def user_playlist_create(self, user, name, public=True, description=""):
        """ Creates a playlist for a user

            Parameters:
                - user - the id of the user
                - name - the name of the playlist
                - public - is the created playlist public
                - description - the description of the playlist
        """
        data = {"name": name, "public": public, "description": description}

        return self._post("users/%s/playlists" % (user,), payload=data)

    def user_playlist_change_details(
        self,
        user,
        playlist_id,
        name=None,
        public=None,
        collaborative=None,
        description=None,
    ):
        """ Changes a playlist's name and/or public/private state

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - name - optional name of the playlist
                - public - optional is the playlist public
                - collaborative - optional is the playlist collaborative
                - description - optional description of the playlist
        """

        data = {}
        if isinstance(name, six.string_types):
            data["name"] = name
        if isinstance(public, bool):
            data["public"] = public
        if isinstance(collaborative, bool):
            data["collaborative"] = collaborative
        if isinstance(description, six.string_types):
            data["description"] = description
        return self._put("users/%s/playlists/%s" % (user, playlist_id), payload=data)

    def user_playlist_unfollow(self, user, playlist_id):
        """ Unfollows (deletes) a playlist for a user

            Parameters:
                - user - the id of the user
                - name - the name of the playlist
        """
        return self._delete("users/%s/playlists/%s/followers" % (user, playlist_id))

    def user_playlist_add_tracks(self, user, playlist_id, tracks, position=None):
        """ Adds tracks to a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - a list of track URIs, URLs or IDs
                - position - the position to add the tracks
        """
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in tracks]
        return self._post(
            "users/%s/playlists/%s/tracks" % (user, plid),
            payload=ftracks,
            position=position,
        )

    def user_playlist_replace_tracks(self, user, playlist_id, tracks):
        """ Replace all tracks in a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist
        """
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in tracks]
        payload = {"uris": ftracks}
        return self._put("users/%s/playlists/%s/tracks" % (user, plid), payload=payload)

    def user_playlist_reorder_tracks(
        self,
        user,
        playlist_id,
        range_start,
        insert_before,
        range_length=1,
        snapshot_id=None,
    ):
        """ Reorder tracks in a playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - range_start - the position of the first track to be reordered
                - range_length - optional the number of tracks to be reordered
                                 (default: 1)
                - insert_before - the position where the tracks should be
                                  inserted
                - snapshot_id - optional playlist's snapshot ID
        """
        plid = self._get_id("playlist", playlist_id)
        payload = {
            "range_start": range_start,
            "range_length": range_length,
            "insert_before": insert_before,
        }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._put("users/%s/playlists/%s/tracks" % (user, plid), payload=payload)

    def user_playlist_remove_all_occurrences_of_tracks(
        self, user, playlist_id, tracks, snapshot_id=None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to remove from the playlist
                - snapshot_id - optional id of the playlist snapshot

        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in tracks]
        payload = {"tracks": [{"uri": track} for track in ftracks]}
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete(
            "users/%s/playlists/%s/tracks" % (user, plid), payload=payload
        )

    def user_playlist_remove_specific_occurrences_of_tracks(
        self, user, playlist_id, tracks, snapshot_id=None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - an array of objects containing Spotify URIs of the
                    tracks to remove with their current positions in the
                    playlist.  For example:
                        [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                        { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
                - snapshot_id - optional id of the playlist snapshot
        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = []
        for tr in tracks:
            ftracks.append(
                {
                    "uri": self._get_uri("track", tr["uri"]),
                    "positions": tr["positions"],
                }
            )
        payload = {"tracks": ftracks}
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete(
            "users/%s/playlists/%s/tracks" % (user, plid), payload=payload
        )

    def user_playlist_follow_playlist(self, playlist_owner_id, playlist_id):
        """
        Add the current authenticated user as a follower of a playlist.

        Parameters:
            - playlist_owner_id - the user id of the playlist owner
            - playlist_id - the id of the playlist

        """
        return self._put(
            "users/{}/playlists/{}/followers".format(playlist_owner_id, playlist_id)
        )

    def user_playlist_is_following(self, playlist_owner_id, playlist_id, user_ids):
        """
        Check to see if the given users are following the given playlist

        Parameters:
            - playlist_owner_id - the user id of the playlist owner
            - playlist_id - the id of the playlist
            - user_ids - the ids of the users that you want to check to see
                if they follow the playlist. Maximum: 5 ids.

        """
        endpoint = "users/{}/playlists/{}/followers/contains?ids={}"
        return self._get(
            endpoint.format(playlist_owner_id, playlist_id, ",".join(user_ids))
        )

    def me(self):
        """ Get detailed profile information about the current user.
            An alias for the 'current_user' method.
        """
        return self._get("me/")

    def current_user(self):
        """ Get detailed profile information about the current user.
            An alias for the 'me' method.
        """
        return self.me()

    def current_user_playing_track(self):
        """ Get information about the current users currently playing track.
        """
        return self._get("me/player/currently-playing")

    def current_user_saved_tracks(self, limit=20, offset=0):
        """ Gets a list of the tracks saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of tracks to return
                - offset - the index of the first track to return

        """
        return self._get("me/tracks", limit=limit, offset=offset)

    def current_user_followed_artists(self, limit=20, after=None):
        """ Gets a list of the artists followed by the current authorized user

            Parameters:
                - limit - the number of artists to return
                - after - the last artist ID retrieved from the previous
                          request

        """
        return self._get("me/following", type="artist", limit=limit, after=after)

    def current_user_saved_tracks_delete(self, tracks=None):
        """ Remove one or more tracks from the current user's
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._delete("me/tracks/?ids=" + ",".join(tlist))

    def current_user_saved_tracks_contains(self, tracks=None):
        """ Check if one or more tracks is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._get("me/tracks/contains?ids=" + ",".join(tlist))

    def current_user_saved_tracks_add(self, tracks=None):
        """ Add one or more tracks to the current user's
            "Your Music" library.

            Parameters:
                - tracks - a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._put("me/tracks/?ids=" + ",".join(tlist))

    def current_user_top_artists(self, limit=20, offset=0, time_range="medium_term"):
        """ Get the current user's top artists

            Parameters:
                - limit - the number of entities to return
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed
                  Valid-values: short_term, medium_term, long_term
        """
        return self._get(
            "me/top/artists", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_top_tracks(self, limit=20, offset=0, time_range="medium_term"):
        """ Get the current user's top tracks

            Parameters:
                - limit - the number of entities to return
                - offset - the index of the first entity to return
                - time_range - Over what time frame are the affinities computed
                  Valid-values: short_term, medium_term, long_term
        """
        return self._get(
            "me/top/tracks", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_recently_played(self, limit=50, after=None, before=None):
        """ Get the current user's recently played tracks

            Parameters:
                - limit - the number of entities to return
                - after - unix timestamp in milliseconds. Returns all items
                          after (but not including) this cursor position.
                          Cannot be used if before is specified.
                - before - unix timestamp in milliseconds. Returns all items
                           before (but not including) this cursor position.
                           Cannot be used if after is specified
        """
        return self._get(
            "me/player/recently-played", limit=limit, after=after, before=before
        )

    def current_user_saved_albums(self, limit=20, offset=0):
        """ Gets a list of the albums saved in the current authorized user's
            "Your Music" library

            Parameters:
                - limit - the number of albums to return
                - offset - the index of the first album to return

        """
        return self._get("me/albums", limit=limit, offset=offset)

    def current_user_saved_albums_contains(self, albums=[]):
        """ Check if one or more albums is already saved in
            the current Spotify user’s “Your Music” library.

            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        alist = [self._get_id("album", a) for a in albums]
        return self._get("me/albums/contains?ids=" + ",".join(alist))

    def current_user_saved_albums_add(self, albums=[]):
        """ Add one or more albums to the current user's
            "Your Music" library.
            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        alist = [self._get_id("album", a) for a in albums]
        return self._put("me/albums?ids=" + ",".join(alist))

    def current_user_saved_albums_delete(self, albums=[]):
        """ Remove one or more albums from the current user's
            "Your Music" library.

            Parameters:
                - albums - a list of album URIs, URLs or IDs
        """
        alist = [self._get_id("album", a) for a in albums]
        return self._delete("me/albums/?ids=" + ",".join(alist))

    def user_follow_artists(self, ids=[]):
        """ Follow one or more artists
            Parameters:
                - ids - a list of artist IDs
        """
        return self._put("me/following?type=artist&ids=" + ",".join(ids))

    def user_follow_users(self, ids=[]):
        """ Follow one or more users
            Parameters:
                - ids - a list of user IDs
        """
        return self._put("me/following?type=user&ids=" + ",".join(ids))

    def user_unfollow_artists(self, ids=[]):
        """ Unfollow one or more artists
            Parameters:
                - ids - a list of artist IDs
        """
        return self._delete("me/following?type=artist&ids=" + ",".join(ids))

    def user_unfollow_users(self, ids=[]):
        """ Unfollow one or more users
            Parameters:
                - ids - a list of user IDs
        """
        return self._delete("me/following?type=user&ids=" + ",".join(ids))

    def featured_playlists(
        self, locale=None, country=None, timestamp=None, limit=20, offset=0
    ):
        """ Get a list of Spotify featured playlists

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
        """
        return self._get(
            "browse/featured-playlists",
            locale=locale,
            country=country,
            timestamp=timestamp,
            limit=limit,
            offset=offset,
        )

    def new_releases(self, country=None, limit=20, offset=0):
        """ Get a list of new album releases featured in Spotify

            Parameters:
                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        return self._get(
            "browse/new-releases", country=country, limit=limit, offset=offset
        )

    def categories(self, country=None, locale=None, limit=20, offset=0):
        """ Get a list of new album releases featured in Spotify

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
        """
        return self._get(
            "browse/categories",
            country=country,
            locale=locale,
            limit=limit,
            offset=offset,
        )

    def category_playlists(self, category_id=None, country=None, limit=20, offset=0):
        """ Get a list of new album releases featured in Spotify

            Parameters:
                - category_id - The Spotify category ID for the category.

                - country - An ISO 3166-1 alpha-2 country code.

                - limit - The maximum number of items to return. Default: 20.
                  Minimum: 1. Maximum: 50

                - offset - The index of the first item to return. Default: 0
                  (the first object). Use with limit to get the next set of
                  items.
        """
        return self._get(
            "browse/categories/" + category_id + "/playlists",
            country=country,
            limit=limit,
            offset=offset,
        )

    def recommendations(
        self,
        seed_artists=None,
        seed_genres=None,
        seed_tracks=None,
        limit=20,
        country=None,
        **kwargs
    ):
        """ Get a list of recommended tracks for one to five seeds.

            Parameters:
                - seed_artists - a list of artist IDs, URIs or URLs

                - seed_tracks - a list of track IDs, URIs or URLs

                - seed_genres - a list of genre names. Available genres for
                                recommendations can be found by calling
                                recommendation_genre_seeds

                - country - An ISO 3166-1 alpha-2 country code. If provided,
                            all results will be playable in this country.

                - limit - The maximum number of items to return. Default: 20.
                          Minimum: 1. Maximum: 100

                - min/max/target_<attribute> - For the tuneable track
                    attributes listed in the documentation, these values
                    provide filters and targeting on results.
        """
        params = dict(limit=limit)
        if seed_artists:
            params["seed_artists"] = ",".join(
                [self._get_id("artist", a) for a in seed_artists]
            )
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres)
        if seed_tracks:
            params["seed_tracks"] = ",".join(
                [self._get_id("track", t) for t in seed_tracks]
            )
        if country:
            params["market"] = country

        for attribute in [
            "acousticness",
            "danceability",
            "duration_ms",
            "energy",
            "instrumentalness",
            "key",
            "liveness",
            "loudness",
            "mode",
            "popularity",
            "speechiness",
            "tempo",
            "time_signature",
            "valence",
        ]:
            for prefix in ["min_", "max_", "target_"]:
                param = prefix + attribute
                if param in kwargs:
                    params[param] = kwargs[param]
        return self._get("recommendations", **params)

    def recommendation_genre_seeds(self):
        """ Get a list of genres available for the recommendations function.
        """
        return self._get("recommendations/available-genre-seeds")

    def audio_analysis(self, track_id):
        """ Get audio analysis for a track based upon its Spotify ID
            Parameters:
                - track_id - a track URI, URL or ID
        """
        trid = self._get_id("track", track_id)
        return self._get("audio-analysis/" + trid)

    def audio_features(self, tracks=[]):
        """ Get audio features for one or multiple tracks based upon their Spotify IDs
            Parameters:
                - tracks - a list of track URIs, URLs or IDs, maximum: 50 ids
        """
        if isinstance(tracks, str):
            trackid = self._get_id("track", tracks)
            results = self._get("audio-features/?ids=" + trackid)
        else:
            tlist = [self._get_id("track", t) for t in tracks]
            results = self._get("audio-features/?ids=" + ",".join(tlist))
        # the response has changed, look for the new style first, and if
        # its not there, fallback on the old style
        if "audio_features" in results:
            return results["audio_features"]
        else:
            return results

    def devices(self):
        """ Get a list of user's available devices.
        """
        return self._get("me/player/devices")

    def current_playback(self, market=None):
        """ Get information about user's current playback.

            Parameters:
                - market - an ISO 3166-1 alpha-2 country code.
        """
        return self._get("me/player", market=market)

    def currently_playing(self, market=None):
        """ Get user's currently playing track.

            Parameters:
                - market - an ISO 3166-1 alpha-2 country code.
        """
        return self._get("me/player/currently-playing", market=market)

    def transfer_playback(self, device_id, force_play=True):
        """ Transfer playback to another device.
            Note that the API accepts a list of device ids, but only
            actually supports one.

            Parameters:
                - device_id - transfer playback to this device
                - force_play - true: after transfer, play. false:
                               keep current state.
        """
        data = {"device_ids": [device_id], "play": force_play}
        return self._put("me/player", payload=data)

    def start_playback(self, device_id=None, context_uri=None, uris=None, offset=None):
        """ Start or resume user's playback.

            Provide a `context_uri` to start playback or a album,
            artist, or playlist.

            Provide a `uris` list to start playback of one or more
            tracks.

            Provide `offset` as {"position": <int>} or {"uri": "<track uri>"}
            to start playback at a particular offset.

            Parameters:
                - device_id - device target for playback
                - context_uri - spotify context uri to play
                - uris - spotify track uris
                - offset - offset into context by index or track
        """
        if context_uri is not None and uris is not None:
            self._warn("specify either context uri or uris, not both")
            return
        if uris is not None and not isinstance(uris, list):
            self._warn("uris must be a list")
            return
        data = {}
        if context_uri is not None:
            data["context_uri"] = context_uri
        if uris is not None:
            data["uris"] = uris
        if offset is not None:
            data["offset"] = offset
        return self._put(
            self._append_device_id("me/player/play", device_id), payload=data
        )

    def pause_playback(self, device_id=None):
        """ Pause user's playback.

            Parameters:
                - device_id - device target for playback
        """
        return self._put(self._append_device_id("me/player/pause", device_id))

    def next_track(self, device_id=None):
        """ Skip user's playback to next track.

            Parameters:
                - device_id - device target for playback
        """
        return self._post(self._append_device_id("me/player/next", device_id))

    def previous_track(self, device_id=None):
        """ Skip user's playback to previous track.

            Parameters:
                - device_id - device target for playback
        """
        return self._post(self._append_device_id("me/player/previous", device_id))

    def seek_track(self, position_ms, device_id=None):
        """ Seek to position in current track.

            Parameters:
                - position_ms - position in milliseconds to seek to
                - device_id - device target for playback
        """
        if not isinstance(position_ms, int):
            self._warn("position_ms must be an integer")
            return
        return self._put(
            self._append_device_id(
                "me/player/seek?position_ms=%s" % position_ms, device_id
            )
        )

    def repeat(self, state, device_id=None):
        """ Set repeat mode for playback.

            Parameters:
                - state - `track`, `context`, or `off`
                - device_id - device target for playback
        """
        if state not in ["track", "context", "off"]:
            self._warn("invalid state")
            return
        self._put(
            self._append_device_id("me/player/repeat?state=%s" % state, device_id)
        )

    def volume(self, volume_percent, device_id=None):
        """ Set playback volume.

            Parameters:
                - volume_percent - volume between 0 and 100
                - device_id - device target for playback
        """
        if not isinstance(volume_percent, int):
            self._warn("volume must be an integer")
            return
        if volume_percent < 0 or volume_percent > 100:
            self._warn("volume must be between 0 and 100, inclusive")
            return
        self._put(
            self._append_device_id(
                "me/player/volume?volume_percent=%s" % volume_percent, device_id
            )
        )

    def shuffle(self, state, device_id=None):
        """ Toggle playback shuffling.

            Parameters:
                - state - true or false
                - device_id - device target for playback
        """
        if not isinstance(state, bool):
            self._warn("state must be a boolean")
            return
        state = str(state).lower()
        self._put(
            self._append_device_id("me/player/shuffle?state=%s" % state, device_id)
        )

    def _append_device_id(self, path, device_id):
        """ Append device ID to API path.

            Parameters:
                - device_id - device id to append
        """
        if device_id:
            if "?" in path:
                path += "&device_id=%s" % device_id
            else:
                path += "?device_id=%s" % device_id
        return path

    def _get_id(self, type, id):
        fields = id.split(":")
        if len(fields) >= 3:
            if type != fields[-2]:
                self._warn(
                    "expected id of type %s but found type %s %s"
                    % (type, fields[-2], id)
                )
            return fields[-1]
        fields = id.split("/")
        if len(fields) >= 3:
            itype = fields[-2]
            if type != itype:
                self._warn(
                    "expected id of type %s but found type %s %s" % (type, itype, id)
                )
            return fields[-1].split("?")[0]
        return id

    def _get_uri(self, type, id):
        return "spotify:" + type + ":" + self._get_id(type, id)


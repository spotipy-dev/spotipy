# -*- coding: utf-8 -*-

""" A simple and thin Python library for the Spotify Web API """

__all__ = ["Spotify", "SpotifyException"]

import json
import logging
import warnings

import requests
import six
import urllib3

from spotipy.exceptions import SpotifyException

logger = logging.getLogger(__name__)


class Spotify(object):
    """
        Example usage::

            import spotipy

            urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
            sp = spotipy.Spotify()

            artist = sp.artist(urn)
            print(artist)

            user = sp.user('plamere')
            print(user)
    """
    max_retries = 3
    default_retry_codes = (429, 500, 502, 503, 504)
    country_codes = [
        "AD",
        "AR",
        "AU",
        "AT",
        "BE",
        "BO",
        "BR",
        "BG",
        "CA",
        "CL",
        "CO",
        "CR",
        "CY",
        "CZ",
        "DK",
        "DO",
        "EC",
        "SV",
        "EE",
        "FI",
        "FR",
        "DE",
        "GR",
        "GT",
        "HN",
        "HK",
        "HU",
        "IS",
        "ID",
        "IE",
        "IT",
        "JP",
        "LV",
        "LI",
        "LT",
        "LU",
        "MY",
        "MT",
        "MX",
        "MC",
        "NL",
        "NZ",
        "NI",
        "NO",
        "PA",
        "PY",
        "PE",
        "PH",
        "PL",
        "PT",
        "SG",
        "ES",
        "SK",
        "SE",
        "CH",
        "TW",
        "TR",
        "GB",
        "US",
        "UY"]

    def __init__(
        self,
        auth=None,
        requests_session=True,
        client_credentials_manager=None,
        oauth_manager=None,
        auth_manager=None,
        proxies=None,
        requests_timeout=5,
        status_forcelist=None,
        retries=max_retries,
        status_retries=max_retries,
        backoff_factor=0.3,
        language=None,
    ):
        """
        Creates a Spotify API client.

        :param auth: An access token (optional)
        :param requests_session:
            A Requests session object or a truthy value to create one.
            A falsy value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons (connection pooling).
        :param client_credentials_manager:
            SpotifyClientCredentials object
        :param oauth_manager:
            SpotifyOAuth object
        :param auth_manager:
            SpotifyOauth, SpotifyClientCredentials,
            or SpotifyImplicitGrant object
        :param proxies:
            Definition of proxies (optional).
            See Requests doc https://2.python-requests.org/en/master/user/advanced/#proxies
        :param requests_timeout:
            Tell Requests to stop waiting for a response after a given
            number of seconds
        :param status_forcelist:
            Tell requests what type of status codes retries should occur on
        :param retries:
            Total number of retries to allow
        :param status_retries:
            Number of times to retry on bad status codes
        :param backoff_factor:
            A backoff factor to apply between attempts after the second try
            See urllib3 https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
        :param language:
            The language parameter advertises what language the user prefers to see.
            See ISO-639-1 language code: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        """
        self.prefix = "https://api.spotify.com/v1/"
        self._auth = auth
        self.client_credentials_manager = client_credentials_manager
        self.oauth_manager = oauth_manager
        self.auth_manager = auth_manager
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.backoff_factor = backoff_factor
        self.retries = retries
        self.status_retries = status_retries
        self.language = language

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._build_session()
            else:  # Use the Requests API module as a "session".
                self._session = requests.api

    def set_auth(self, auth):
        self._auth = auth

    @property
    def auth_manager(self):
        return self._auth_manager

    @auth_manager.setter
    def auth_manager(self, auth_manager):
        if auth_manager is not None:
            self._auth_manager = auth_manager
        else:
            self._auth_manager = (
                self.client_credentials_manager or self.oauth_manager
            )

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _build_session(self):
        self._session = requests.Session()
        retry = urllib3.Retry(
            total=self.retries,
            connect=None,
            read=False,
            allowed_methods=frozenset(['GET', 'POST', 'PUT', 'DELETE']),
            status=self.status_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist)

        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)

    def _auth_headers(self):
        if self._auth:
            return {"Authorization": "Bearer {0}".format(self._auth)}
        if not self.auth_manager:
            return {}
        try:
            token = self.auth_manager.get_access_token(as_dict=False)
        except TypeError:
            token = self.auth_manager.get_access_token()
        return {"Authorization": "Bearer {0}".format(token)}

    def _internal_call(self, method, url, payload, params):
        args = dict(params=params)
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

        if self.language is not None:
            headers["Accept-Language"] = self.language

        logger.debug('Sending %s to %s with Params: %s Headers: %s and Body: %r ',
                     method, url, args.get("params"), headers, args.get('data'))

        try:
            response = self._session.request(
                method, url, headers=headers, proxies=self.proxies,
                timeout=self.requests_timeout, **args
            )

            response.raise_for_status()
            results = response.json()
        except requests.exceptions.HTTPError as http_error:
            response = http_error.response
            try:
                json_response = response.json()
                error = json_response.get("error", {})
                msg = error.get("message")
                reason = error.get("reason")
            except ValueError:
                # if the response cannot be decoded into JSON (which raises a ValueError),
                # then try to decode it into text

                # if we receive an empty string (which is falsy), then replace it with `None`
                msg = response.text or None
                reason = None

            logger.error(
                'HTTP Error for %s to %s with Params: %s returned %s due to %s',
                method, url, args.get("params"), response.status_code, msg
            )

            raise SpotifyException(
                response.status_code,
                -1,
                "%s:\n %s" % (response.url, msg),
                reason=reason,
                headers=response.headers,
            )
        except requests.exceptions.RetryError as retry_error:
            request = retry_error.request
            logger.error('Max Retries reached')
            try:
                reason = retry_error.args[0].reason
            except (IndexError, AttributeError):
                reason = None
            raise SpotifyException(
                429,
                -1,
                "%s:\n %s" % (request.path_url, "Max Retries"),
                reason=reason
            )
        except ValueError:
            results = None

        logger.debug('RESULTS: %s', results)
        return results

    def _get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)

        return self._internal_call("GET", url, payload, kwargs)

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

    def next(self, result: dict):
        """ returns the next result given a paged result

            :param result: a previously returned paged result
        """
        if result["next"]:
            return self._get(result["next"])
        else:
            return None

    def previous(self, result: dict):
        """ returns the previous result given a paged result

            :param result: a previously returned paged result
        """
        if result["previous"]:
            return self._get(result["previous"])
        else:
            return None

    def track(self, track_id: str, market: str = None):
        """ returns a single track given the track's ID, URI or URL

            :param track_id: a spotify URI, URL or ID
            :param market: an ISO 3166-1 alpha-2 country code.
        """

        trid = self._get_id("track", track_id)
        return self._get("tracks/" + trid, market=market)

    def tracks(self, tracks: list, market: str = None):
        """ returns a list of tracks given a list of track IDs, URIs, or URLs

            :param tracks: a list of spotify URIs, URLs or IDs. Maximum: 50 IDs.
            :param market: an ISO 3166-1 alpha-2 country code.
        """

        tlist = [self._get_id("track", t) for t in tracks]
        return self._get("tracks/?ids=" + ",".join(tlist), market=market)

    def artist(self, artist_id: str):
        """ returns a single artist given the artist's ID, URI or URL

            :param artist_id: an artist ID, URI or URL
        """

        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid)

    def artists(self, artists: list):
        """ returns a list of artists given the artist IDs, URIs, or URLs

            :param artists: a list of  artist IDs, URIs or URLs
        """

        tlist = [self._get_id("artist", a) for a in artists]
        return self._get("artists/?ids=" + ",".join(tlist))

    def artist_albums(
        self, artist_id: str, album_type: str = None, country: str = None, limit: int = 20, offset: int = 0
    ):
        """ Get Spotify catalog information about an artist's albums

            :param artist_id: the artist ID, URI or URL
            :param album_type: 'album', 'single', 'appears_on', 'compilation'
            :param country: limit the response to one particular country.
            :param limit: the number of albums to return
            :param offset: the index of the first album to return
        """

        trid = self._get_id("artist", artist_id)
        return self._get(
            "artists/" + trid + "/albums",
            album_type=album_type,
            country=country,
            limit=limit,
            offset=offset,
        )

    def artist_top_tracks(self, artist_id: str, country: str = "US"):
        """ Get Spotify catalog information about an artist's top 10 tracks
            by country.

            :param artist_id: the artist ID, URI or URL
            :param country: limit the response to one particular country.
        """

        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid + "/top-tracks", country=country)

    def artist_related_artists(self, artist_id: str):
        """ Get Spotify catalog information about artists similar to an
            identified artist. Similarity is based on analysis of the
            Spotify community's listening history.

            :param artist_id: the artist ID, URI or URL
        """
        trid = self._get_id("artist", artist_id)
        return self._get("artists/" + trid + "/related-artists")

    def album(self, album_id: str, market: str = None):
        """ returns a single album given the album's ID, URIs or URL

            :param album_id: the album ID, URI or URL
            :param market: an ISO 3166-1 alpha-2 country code
        """

        trid = self._get_id("album", album_id)
        if market is not None:
            return self._get("albums/" + trid + '?market=' + market)
        else:
            return self._get("albums/" + trid)

    def album_tracks(self, album_id: str, limit: int = 50, offset: int = 0, market: str = None):
        """ Get Spotify catalog information about an album's tracks

            :param album_id: the album ID, URI or URL
            :param limit: the number of items to return
            :param offset: the index of the first item to return
            :param market: an ISO 3166-1 alpha-2 country code.

        """

        trid = self._get_id("album", album_id)
        return self._get(
            "albums/" + trid + "/tracks/", limit=limit, offset=offset, market=market
        )

    def albums(self, albums: list, market: str = None):
        """ returns a list of albums given the album IDs, URIs, or URLs

            :param albums: a list of  album IDs, URIs or URLs
            :param market: an ISO 3166-1 alpha-2 country code
        """

        tlist = [self._get_id("album", a) for a in albums]
        if market is not None:
            return self._get("albums/?ids=" + ",".join(tlist) + '&market=' + market)
        else:
            return self._get("albums/?ids=" + ",".join(tlist))

    def show(self, show_id: str, market: str = None):
        """ returns a single show given the show's ID, URIs or URL

            :param show_id: the show ID, URI or URL
            :param market: an ISO 3166-1 alpha-2 country code.
                        The show must be available in the given market.
                        If user-based authorization is in use, the user's country
                        takes precedence. If neither market nor user country are
                        provided, the content is considered unavailable for the client.
        """

        trid = self._get_id("show", show_id)
        return self._get("shows/" + trid, market=market)

    def shows(self, shows: list, market: str = None):
        """ returns a list of shows given the show IDs, URIs, or URLs

            :param shows: a list of show IDs, URIs or URLs
            :param market: an ISO 3166-1 alpha-2 country code.
                        Only shows available in the given market will be returned.
                        If user-based authorization is in use, the user's country
                        takes precedence. If neither market nor user country are
                        provided, the content is considered unavailable for the client.
        """

        tlist = [self._get_id("show", s) for s in shows]
        return self._get("shows/?ids=" + ",".join(tlist), market=market)

    def show_episodes(self, show_id: str, limit: int = 50, offset: int = 0, market: str = None):
        """ Get Spotify catalog information about a show's episodes

            :param show_id: the show ID, URI or URL
            :param limit: the number of items to return
            :param offset: the index of the first item to return
            :param market: an ISO 3166-1 alpha-2 country code.
                        Only episodes available in the given market will be returned.
                        If user-based authorization is in use, the user's country
                        takes precedence. If neither market nor user country are
                        provided, the content is considered unavailable for the client.
        """

        trid = self._get_id("show", show_id)
        return self._get(
            "shows/" + trid + "/episodes/", limit=limit, offset=offset, market=market
        )

    def episode(self, episode_id: str, market: str = None):
        """ returns a single episode given the episode's ID, URIs or URL

            :param episode_id: the episode ID, URI or URL
            :param market: an ISO 3166-1 alpha-2 country code.
                        The episode must be available in the given market.
                        If user-based authorization is in use, the user's country
                        takes precedence. If neither market nor user country are
                        provided, the content is considered unavailable for the client.
        """

        trid = self._get_id("episode", episode_id)
        return self._get("episodes/" + trid, market=market)

    def episodes(self, episodes: list, market: str = None):
        """ returns a list of episodes given the episode IDs, URIs, or URLs

            :param episodes: a list of episode IDs, URIs or URLs
            :param market: an ISO 3166-1 alpha-2 country code.
                        Only episodes available in the given market will be returned.
                        If user-based authorization is in use, the user's country
                        takes precedence. If neither market nor user country are
                        provided, the content is considered unavailable for the client.
        """

        tlist = [self._get_id("episode", e) for e in episodes]
        return self._get("episodes/?ids=" + ",".join(tlist), market=market)

    def search(self, q: str, limit: int = 10, offset: int = 0,
               type: str = "track", market: str = None):
        """ searches for an item

            :param q: the search query (see how to write a query in the
                    official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
            :param limit: the number of items to return (min = 1, default = 10, max = 50). The limit is applied
                        within each type, not on the total response.
            :param offset: the index of the first item to return
            :param type: the types of items to return. One or more of 'artist', 'album',
                        'track', 'playlist', 'show', and 'episode'.  If multiple types are desired,
                        pass in a comma separated string; e.g., 'track,album,episode'.
            :param market: An ISO 3166-1 alpha-2 country code or the string
                        from_token.
        """
        return self._get(
            "search", q=q, limit=limit, offset=offset, type=type, market=market
        )

    def search_markets(self, q: str, limit: int = 10, offset: int = 0,
                       type: str = "track", markets: list = None, total: int = None):
        """ (experimental) Searches multiple markets for an item

            :param q: the search query (see how to write a query in the
                    official documentation https://developer.spotify.com/documentation/web-api/reference/search/)  # noqa
            :param limit: the number of items to return (min = 1, default = 10, max = 50). If a search is to be done on multiple
                        markets, then this limit is applied to each market. (e.g. search US, CA, MX each with a limit of 10).
            :param offset: the index of the first item to return
            :param type: the types of items to return. One or more of 'artist', 'album',
                        'track', 'playlist', 'show', or 'episode'. If multiple types are desired, pass in a comma separated string.
            :param markets: A list of ISO 3166-1 alpha-2 country codes. Search all country markets by default.
            :param total: the total number of results to return if multiple markets are supplied in the search.
                        If multiple types are specified, this only applies to the first type.
        """
        warnings.warn(
            "Searching multiple markets is an experimental feature. "
            "Please be aware that this method's inputs and outputs can change in the future.",
            UserWarning,
        )
        if not markets:
            markets = self.country_codes

        if not (isinstance(markets, list) or isinstance(markets, tuple)):
            markets = []

        warnings.warn(
            "Searching multiple markets is poorly performing.",
            UserWarning,
        )
        return self._search_multiple_markets(q, limit, offset, type, markets, total)

    def user(self, user: str):
        """ Gets basic profile information about a Spotify User

            :param user: the id of the user
        """
        return self._get("users/" + user)

    def current_user_playlists(self, limit: int = 50, offset: int = 0):
        """ Get current user playlists without required getting his profile

            :param limit: the number of items to return
            :param offset: the index of the first item to return
        """
        return self._get("me/playlists", limit=limit, offset=offset)

    def playlist(self, playlist_id: str, fields: str = None,
                 market: str = None, additional_types: tuple = ("track",)):
        """ Gets playlist by id.

            :param playlist_id: the id of the playlist
            :param fields: which fields to return
            :param market: An ISO 3166-1 alpha-2 country code or the
                        string from_token.
            :param additional_types: list of item types to return.
                                    valid types are: track and episode
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(
            "playlists/%s" % (plid),
            fields=fields,
            market=market,
            additional_types=",".join(additional_types),
        )

    def playlist_tracks(
        self,
        playlist_id: str,
        fields: str = None,
        limit: int = 100,
        offset: int = 0,
        market: str = None,
        additional_types: tuple = ("track",)
    ):
        """ Get full details of the tracks of a playlist.

            :param playlist_id: the playlist ID, URI or URL
            :param fields: which fields to return
            :param limit: the maximum number of tracks to return
            :param offset: the index of the first track to return
            :param market: an ISO 3166-1 alpha-2 country code.
            :param additional_types: list of item types to return.
                                    valid types are: track and episode
        """
        warnings.warn(
            "You should use `playlist_items(playlist_id, ...,"
            "additional_types=('track',))` instead",
            DeprecationWarning,
        )
        return self.playlist_items(playlist_id, fields, limit, offset,
                                   market, additional_types)

    def playlist_items(
        self,
        playlist_id: str,
        fields: str = None,
        limit: int = 100,
        offset: int = 0,
        market: str = None,
        additional_types: tuple = ("track", "episode")
    ):
        """ Get full details of the tracks and episodes of a playlist.

            :param playlist_id: the playlist ID, URI or URL
            :param fields: which fields to return
            :param limit: the maximum number of tracks to return
            :param offset: the index of the first track to return
            :param market: an ISO 3166-1 alpha-2 country code.
            :param additional_types: list of item types to return.
                                    valid types are: track and episode
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(
            "playlists/%s/tracks" % (plid),
            limit=limit,
            offset=offset,
            fields=fields,
            market=market,
            additional_types=",".join(additional_types)
        )

    def playlist_cover_image(self, playlist_id: str):
        """ Get cover image of a playlist.

            :param playlist_id: the playlist ID, URI or URL
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get("playlists/%s/images" % (plid))

    def playlist_upload_cover_image(self, playlist_id: str, image_b64: str):
        """ Replace the image used to represent a specific playlist

            :param playlist_id: the id of the playlist
            :param image_b64: image data as a Base64 encoded JPEG image string
                (maximum payload size is 256 KB)
        """
        plid = self._get_id("playlist", playlist_id)
        return self._put(
            "playlists/{}/images".format(plid),
            payload=image_b64,
            content_type="image/jpeg",
        )

    def user_playlist(self, user, playlist_id: str = None, fields: str = None, market: str = None):
        warnings.warn(
            "You should use `playlist(playlist_id)` instead",
            DeprecationWarning,
        )

        """ Gets a single playlist of a user

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param fields: which fields to return
        """
        if playlist_id is None:
            return self._get("users/%s/starred" % user)
        return self.playlist(playlist_id, fields=fields, market=market)

    def user_playlist_tracks(
        self,
        user: str = None,
        playlist_id: str = None,
        fields: str = None,
        limit: int = 100,
        offset: int = 0,
        market: str = None,
    ):
        warnings.warn(
            "You should use `playlist_tracks(playlist_id)` instead",
            DeprecationWarning,
        )

        """ Get full details of the tracks of a playlist owned by a user.

                :param user: the id of the user
                :param playlist_id: the id of the playlist
                :param fields: which fields to return
                :param limit: the maximum number of tracks to return
                :param offset: the index of the first track to return
                :param market: an ISO 3166-1 alpha-2 country code.
        """
        return self.playlist_tracks(
            playlist_id,
            limit=limit,
            offset=offset,
            fields=fields,
            market=market,
        )

    def user_playlists(self, user: str, limit: int = 50, offset: int = 0):
        """ Gets playlists of a user

            :param user: the id of the usr
            :param limit: the number of items to return
            :param offset: the index of the first item to return
        """
        return self._get(
            "users/%s/playlists" % user, limit=limit, offset=offset
        )

    def user_playlist_create(self, user: str, name: str, public: bool = True,
                             collaborative: bool = False, description: str = ""):
        """ Creates a playlist for a user

            :param user: the id of the user
            :param name: the name of the playlist
            :param public: is the created playlist public
            :param collaborative: is the created playlist collaborative
            :param description: the description of the playlist
        """
        data = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
            "description": description
        }

        return self._post("users/%s/playlists" % (user,), payload=data)

    def user_playlist_change_details(
        self,
        user: str,
        playlist_id: str,
        name: str = None,
        public: bool = None,
        collaborative: bool = None,
        description: str = None,
    ):
        warnings.warn(
            "You should use `playlist_change_details(playlist_id, ...)` instead",
            DeprecationWarning,
        )
        """ Changes a playlist's name and/or public/private state

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param name: optional name of the playlist
            :param public: optional is the playlist public
            :param collaborative: optional is the playlist collaborative
            :param description: optional description of the playlist
        """

        return self.playlist_change_details(playlist_id, name, public,
                                            collaborative, description)

    def user_playlist_unfollow(self, user: str, playlist_id: str):
        """ Unfollows (deletes) a playlist for a user

            :param user: the id of the user
            :param playlist_id: id of the playlist
        """
        warnings.warn(
            "You should use `current_user_unfollow_playlist(playlist_id)` instead",
            DeprecationWarning,
        )
        return self.current_user_unfollow_playlist(playlist_id)

    def user_playlist_add_tracks(
        self, user: str, playlist_id: str, tracks: str, position: int = None
    ):
        warnings.warn(
            "You should use `playlist_add_items(playlist_id, tracks)` instead",
            DeprecationWarning,
        )
        """ Adds tracks to a playlist

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param tracks: a list of track URIs, URLs or IDs
            :param position: the position to add the tracks
        """
        return self.playlist_add_items(playlist_id, tracks, position)

    def user_playlist_replace_tracks(self, user: str, playlist_id: str, tracks: list):
        """ Replace all tracks in a playlist for a user

            Parameters:
                - user - the id of the user
                - playlist_id - the id of the playlist
                - tracks - the list of track ids to add to the playlist
        """
        warnings.warn(
            "You should use `playlist_replace_items(playlist_id, tracks)` instead",
            DeprecationWarning,
        )
        return self.playlist_replace_items(playlist_id, tracks)

    def user_playlist_reorder_tracks(
        self,
        user: str,
        playlist_id: str,
        range_start: int,
        insert_before: int,
        range_length: int = 1,
        snapshot_id: str = None,
    ):
        """ Reorder tracks in a playlist from a user

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param range_start: the position of the first track to be reordered
            :param range_length: optional the number of tracks to be reordered
                                (default: 1)
            :param insert_before: the position where the tracks should be
                                inserted
            :param snapshot_id: optional playlist's snapshot ID
        """
        warnings.warn(
            "You should use `playlist_reorder_items(playlist_id, ...)` instead",
            DeprecationWarning,
        )
        return self.playlist_reorder_items(playlist_id, range_start,
                                           insert_before, range_length,
                                           snapshot_id)

    def user_playlist_remove_all_occurrences_of_tracks(
        self, user: str, playlist_id: str, tracks: list, snapshot_id: str = None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param tracks: the list of track ids to remove from the playlist
            :param snapshot_id: optional id of the playlist snapshot

        """
        warnings.warn(
            "You should use `playlist_remove_all_occurrences_of_items"
            "(playlist_id, tracks)` instead",
            DeprecationWarning,
        )
        return self.playlist_remove_all_occurrences_of_items(playlist_id,
                                                             tracks,
                                                             snapshot_id)

    def user_playlist_remove_specific_occurrences_of_tracks(
        self, user: str, playlist_id: str, tracks: list, snapshot_id: str = None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            :param user: the id of the user
            :param playlist_id: the id of the playlist
            :param tracks: an array of objects containing Spotify URIs of the
                tracks to remove with their current positions in the
                playlist.  For example:
                    [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                    { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
            :param snapshot_id: optional id of the playlist snapshot
        """
        warnings.warn(
            "You should use `playlist_remove_specific_occurrences_of_items"
            "(playlist_id, tracks)` instead",
            DeprecationWarning,
        )
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

    def user_playlist_follow_playlist(self, playlist_owner_id: str, playlist_id: str):
        """
        Add the current authenticated user as a follower of a playlist.

        :param playlist_owner_id: the user id of the playlist owner
        :param playlist_id: the id of the playlist

        """
        warnings.warn(
            "You should use `current_user_follow_playlist(playlist_id)` instead",
            DeprecationWarning,
        )
        return self.current_user_follow_playlist(playlist_id)

    def user_playlist_is_following(
        self, playlist_owner_id: str, playlist_id, user_ids: list
    ):
        """
        Check to see if the given users are following the given playlist

        :param playlist_owner_id: the user id of the playlist owner
        :param playlist_id: the id of the playlist
        :param user_ids: the ids of the users that you want to check to see
            if they follow the playlist. Maximum: 5 ids.

        """
        warnings.warn(
            "You should use `playlist_is_following(playlist_id, user_ids)` instead",
            DeprecationWarning,
        )
        return self.playlist_is_following(playlist_id, user_ids)

    def playlist_change_details(
        self,
        playlist_id: str,
        name: str = None,
        public: bool = None,
        collaborative: bool = None,
        description: str = None,
    ):
        """ Changes a playlist's name and/or public/private state,
            collaborative state, and/or description

            :param playlist_id: the id of the playlist
            :param name: optional name of the playlist
            :param public: optional is the playlist public
            :param collaborative: optional is the playlist collaborative
            :param description: optional description of the playlist
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
        return self._put(
            "playlists/%s" % (self._get_id("playlist", playlist_id)), payload=data
        )

    def current_user_unfollow_playlist(self, playlist_id: str):
        """ Unfollows (deletes) a playlist for the current authenticated
            user

            :param playlist_id: the id of the playlist
        """
        return self._delete(
            "playlists/%s/followers" % playlist_id
        )

    def playlist_add_items(
        self, playlist_id: str, items, position: int = None
    ):
        """ Adds tracks/episodes to a playlist

            :param playlist_id: the id of the playlist
            :param items: a list of track/episode URIs, URLs or IDs
            :param position: the position to add the tracks
        """
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in items]
        return self._post(
            "playlists/%s/tracks" % plid,
            payload=ftracks,
            position=position,
        )

    def playlist_replace_items(self, playlist_id: str, items: list):
        """ Replace all tracks/episodes in a playlist

            :param playlist_id: the id of the playlist
            :param items: list of track/episode ids to comprise playlist
        """
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in items]
        payload = {"uris": ftracks}
        return self._put(
            "playlists/%s/tracks" % plid, payload=payload
        )

    def playlist_reorder_items(
        self,
        playlist_id: str,
        range_start: int,
        insert_before: int,
        range_length: int = 1,
        snapshot_id: str = None,
    ):
        """ Reorder tracks in a playlist

            :param playlist_id: the id of the playlist
            :param range_start: the position of the first track to be reordered
            :param range_length: optional the number of tracks to be reordered
                                (default: 1)
            :param insert_before: the position where the tracks should be
                                inserted
            :param snapshot_id: optional playlist's snapshot ID
        """
        plid = self._get_id("playlist", playlist_id)
        payload = {
            "range_start": range_start,
            "range_length": range_length,
            "insert_before": insert_before,
        }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._put(
            "playlists/%s/tracks" % plid, payload=payload
        )

    def playlist_remove_all_occurrences_of_items(
        self, playlist_id: str, items: list, snapshot_id: str = None
    ):
        """ Removes all occurrences of the given tracks/episodes from the given playlist

            :param playlist_id: the id of the playlist
            :param items: list of track/episode ids to remove from the playlist
            :param snapshot_id: optional id of the playlist snapshot

        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in items]
        payload = {"tracks": [{"uri": track} for track in ftracks]}
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete(
            "playlists/%s/tracks" % plid, payload=payload
        )

    def playlist_remove_specific_occurrences_of_items(
        self, playlist_id: str, items: list, snapshot_id: str = None
    ):
        """ Removes all occurrences of the given tracks from the given playlist

            :param playlist_id: the id of the playlist
            :param items: an array of objects containing Spotify URIs of the
                tracks/episodes to remove with their current positions in
                the playlist.  For example:
                    [  { "uri":"4iV5W9uYEdYUVa79Axb7Rh", "positions":[2] },
                    { "uri":"1301WleyT98MSxVHPZCA6M", "positions":[7] } ]
            :param snapshot_id: optional id of the playlist snapshot
        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = []
        for tr in items:
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
            "playlists/%s/tracks" % plid, payload=payload
        )

    def current_user_follow_playlist(self, playlist_id: str):
        """
        Add the current authenticated user as a follower of a playlist.

        :param playlist_id: the id of the playlist

        """
        return self._put(
            "playlists/{}/followers".format(playlist_id)
        )

    def playlist_is_following(
        self, playlist_id: str, user_ids: list
    ):
        """
        Check to see if the given users are following the given playlist

        :param playlist_id: the id of the playlist
        :param user_ids: the ids of the users that you want to check to see
            if they follow the playlist. Maximum: 5 ids.

        """
        endpoint = "playlists/{}/followers/contains?ids={}"
        return self._get(
            endpoint.format(playlist_id, ",".join(user_ids))
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

    def current_user_saved_albums(self, limit: int = 20, offset: int = 0, market: str = None):
        """ Gets a list of the albums saved in the current authorized user's
            "Your Music" library

            :param limit: the number of albums to return (MAX_LIMIT=50)
            :param offset: the index of the first album to return
            :param market: an ISO 3166-1 alpha-2 country code.

        """
        return self._get("me/albums", limit=limit, offset=offset, market=market)

    def current_user_saved_albums_add(self, albums: list = []):
        """ Add one or more albums to the current user's
            "Your Music" library.

            :param albums: a list of album URIs, URLs or IDs
        """

        alist = [self._get_id("album", a) for a in albums]
        return self._put("me/albums?ids=" + ",".join(alist))

    def current_user_saved_albums_delete(self, albums: list = []):
        """ Remove one or more albums from the current user's
            "Your Music" library.

            :param albums: a list of album URIs, URLs or IDs
        """
        alist = [self._get_id("album", a) for a in albums]
        return self._delete("me/albums/?ids=" + ",".join(alist))

    def current_user_saved_albums_contains(self, albums: list = []):
        """ Check if one or more albums is already saved in
            the current Spotify user’s “Your Music” library.

            :param albums: a list of album URIs, URLs or IDs
        """
        alist = [self._get_id("album", a) for a in albums]
        return self._get("me/albums/contains?ids=" + ",".join(alist))

    def current_user_saved_tracks(self, limit: int = 20, offset: int = 0, market: str = None):
        """ Gets a list of the tracks saved in the current authorized user's
            "Your Music" library

            :param limit: the number of tracks to return
            :param offset: the index of the first track to return
            :param market: an ISO 3166-1 alpha-2 country code

        """
        return self._get("me/tracks", limit=limit, offset=offset, market=market)

    def current_user_saved_tracks_add(self, tracks: list = None):
        """ Add one or more tracks to the current user's
            "Your Music" library.

            :param tracks: a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._put("me/tracks/?ids=" + ",".join(tlist))

    def current_user_saved_tracks_delete(self, tracks: list = None):
        """ Remove one or more tracks from the current user's
            "Your Music" library.

            :param tracks: a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._delete("me/tracks/?ids=" + ",".join(tlist))

    def current_user_saved_tracks_contains(self, tracks: list = None):
        """ Check if one or more tracks is already saved in
            the current Spotify user’s “Your Music” library.

            :param tracks: a list of track URIs, URLs or IDs
        """
        tlist = []
        if tracks is not None:
            tlist = [self._get_id("track", t) for t in tracks]
        return self._get("me/tracks/contains?ids=" + ",".join(tlist))

    def current_user_saved_episodes(self, limit: int = 20, offset: int = 0, market: str = None):
        """ Gets a list of the episodes saved in the current authorized user's
            "Your Music" library

            :param limit: the number of episodes to return
            :param offset: the index of the first episode to return
            :param market: an ISO 3166-1 alpha-2 country code

        """
        return self._get("me/episodes", limit=limit, offset=offset, market=market)

    def current_user_saved_episodes_add(self, episodes: list = None):
        """ Add one or more episodes to the current user's
            "Your Music" library.

            :param episodes: a list of episode URIs, URLs or IDs
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._put("me/episodes/?ids=" + ",".join(elist))

    def current_user_saved_episodes_delete(self, episodes: list = None):
        """ Remove one or more episodes from the current user's
            "Your Music" library.

            :param episodes: a list of episode URIs, URLs or IDs
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._delete("me/episodes/?ids=" + ",".join(elist))

    def current_user_saved_episodes_contains(self, episodes: list = None):
        """ Check if one or more episodes is already saved in
            the current Spotify user’s “Your Music” library.

            :param episodes: a list of episode URIs, URLs or IDs
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._get("me/episodes/contains?ids=" + ",".join(elist))

    def current_user_saved_shows(self, limit: int = 20, offset: int = 0, market: str = None):
        """ Gets a list of the shows saved in the current authorized user's
            "Your Music" library

            :param limit: the number of shows to return
            :param offset: the index of the first show to return
            :param market: an ISO 3166-1 alpha-2 country code

        """
        return self._get("me/shows", limit=limit, offset=offset, market=market)

    def current_user_saved_shows_add(self, shows: list = []):
        """ Add one or more albums to the current user's
            "Your Music" library.

            :param shows: a list of show URIs, URLs or IDs
        """
        slist = [self._get_id("show", s) for s in shows]
        return self._put("me/shows?ids=" + ",".join(slist))

    def current_user_saved_shows_delete(self, shows: list = []):
        """ Remove one or more shows from the current user's
            "Your Music" library.

            :param shows: a list of show URIs, URLs or IDs
        """
        slist = [self._get_id("show", s) for s in shows]
        return self._delete("me/shows/?ids=" + ",".join(slist))

    def current_user_saved_shows_contains(self, shows: list = []):
        """ Check if one or more shows is already saved in
            the current Spotify user’s “Your Music” library.

            :param shows: a list of show URIs, URLs or IDs
        """
        slist = [self._get_id("show", s) for s in shows]
        return self._get("me/shows/contains?ids=" + ",".join(slist))

    def current_user_followed_artists(self, limit: int = 20, after: str = None):
        """ Gets a list of the artists followed by the current authorized user

            :param limit: the number of artists to return
            :param after: the last artist ID retrieved from the previous request

        """
        return self._get(
            "me/following", type="artist", limit=limit, after=after
        )

    def current_user_following_artists(self, ids: list = None):
        """ Check if the current user is following certain artists

            Returns list of booleans respective to ids

            :param ids: a list of artist URIs, URLs or IDs
        """
        idlist = []
        if ids is not None:
            idlist = [self._get_id("artist", i) for i in ids]
        return self._get(
            "me/following/contains", ids=",".join(idlist), type="artist"
        )

    def current_user_following_users(self, ids: list = None):
        """ Check if the current user is following certain users

            Returns list of booleans respective to ids

            :param ids: a list of user URIs, URLs or IDs
        """
        idlist = []
        if ids is not None:
            idlist = [self._get_id("user", i) for i in ids]
        return self._get(
            "me/following/contains", ids=",".join(idlist), type="user"
        )

    def current_user_top_artists(
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ):
        """ Get the current user's top artists

            :param limit: the number of entities to return
            :param offset: the index of the first entity to return
            :param time_range: Over what time frame are the affinities computed
                Valid-values: short_term, medium_term, long_term
        """
        return self._get(
            "me/top/artists", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_top_tracks(
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ):
        """ Get the current user's top tracks

            :param limit: the number of entities to return
            :param offset: the index of the first entity to return
            :param time_range: Over what time frame are the affinities computed
                Valid-values: short_term, medium_term, long_term
        """
        return self._get(
            "me/top/tracks", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_recently_played(self, limit: int = 50, after: int = None, before: int = None):
        """ Get the current user's recently played tracks

            :param limit: the number of entities to return
            :param after: unix timestamp in milliseconds. Returns all items
                        after (but not including) this cursor position.
                        Cannot be used if before is specified.
            :param before: unix timestamp in milliseconds. Returns all items
                        before (but not including) this cursor position.
                        Cannot be used if after is specified
        """
        return self._get(
            "me/player/recently-played",
            limit=limit,
            after=after,
            before=before,
        )

    def user_follow_artists(self, ids: list = []):
        """ Follow one or more artists

            :param ids: a list of artist IDs
        """
        return self._put("me/following?type=artist&ids=" + ",".join(ids))

    def user_follow_users(self, ids: list = []):
        """ Follow one or more users

            :param ids: a list of user IDs
        """
        return self._put("me/following?type=user&ids=" + ",".join(ids))

    def user_unfollow_artists(self, ids: list = []):
        """ Unfollow one or more artists

            :param ids: a list of artist IDs
        """
        return self._delete("me/following?type=artist&ids=" + ",".join(ids))

    def user_unfollow_users(self, ids: list = []):
        """ Unfollow one or more users

            :param ids: a list of user IDs
        """
        return self._delete("me/following?type=user&ids=" + ",".join(ids))

    def featured_playlists(
        self, locale: str = None, country: str = None, timestamp: str = None, limit: int = 20, offset: int = 0
    ):
        """ Get a list of Spotify featured playlists

            :param locale: The desired language, consisting of a lowercase ISO
                639-1 alpha-2 language code and an uppercase ISO 3166-1 alpha-2
                country code, joined by an underscore.

            :param country: An ISO 3166-1 alpha-2 country code.

            :param timestamp: A timestamp in ISO 8601 format:
                yyyy-MM-ddTHH:mm:ss. Use this parameter to specify the user's
                local time to get results tailored for that specific date and
                time in the day

            :param limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50

            :param offset: The index of the first item to return. Default: 0
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

    def new_releases(self, country: str = None, limit: int = 20, offset: int = 0):
        """ Get a list of new album releases featured in Spotify

            :param country: An ISO 3166-1 alpha-2 country code.

            :param limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50

            :param offset: The index of the first item to return. Default: 0
                (the first object). Use with limit to get the next set of
                items.
        """
        return self._get(
            "browse/new-releases", country=country, limit=limit, offset=offset
        )

    def category(self, category_id: str, country: str = None, locale: str = None):
        """ Get info about a category

            :param category_id: The Spotify category ID for the category.

            :param country: An ISO 3166-1 alpha-2 country code.
            :param locale: The desired language, consisting of an ISO 639-1 alpha-2
                language code and an ISO 3166-1 alpha-2 country code, joined
                by an underscore.
        """
        return self._get(
            "browse/categories/" + category_id,
            country=country,
            locale=locale,
        )

    def categories(self, country: str = None, locale: str = None,
                   limit: int = 20, offset: int = 0):
        """ Get a list of categories

            country: An ISO 3166-1 alpha-2 country code.
            locale: The desired language, consisting of an ISO 639-1 alpha-2
                language code and an ISO 3166-1 alpha-2 country code, joined
                by an underscore.

            limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50

            offset: The index of the first item to return. Default: 0
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

    def category_playlists(
        self, category_id: str = None, country: str = None, limit: int = 20, offset: int = 0
    ):
        """ Get a list of playlists for a specific Spotify category

            :param category_id: The Spotify category ID for the category.

            :param country: An ISO 3166-1 alpha-2 country code.

            :param limit: The maximum number of items to return. Default: 20.
                Minimum: 1. Maximum: 50

            :param offset: The index of the first item to return. Default: 0
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
        seed_artists: list = None,
        seed_genres: list = None,
        seed_tracks: list = None,
        limit: int = 20,
        country: str = None,
        **kwargs
    ):
        """ Get a list of recommended tracks for one to five seeds.
            (at least one of `seed_artists`, `seed_tracks` and `seed_genres`
            are needed)

            :param seed_artists: a list of artist IDs, URIs or URLs
            :param seed_tracks: a list of track IDs, URIs or URLs
            :param seed_genres: a list of genre names. Available genres for
                            recommendations can be found by calling
                            recommendation_genre_seeds

            :param country: An ISO 3166-1 alpha-2 country code. If provided,
                        all results will be playable in this country.

            :param limit: The maximum number of items to return. Default: 20.
                        Minimum: 1. Maximum: 100

            :param min/max/target_<attribute>: For the tuneable track
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

    def audio_analysis(self, track_id: str):
        """ Get audio analysis for a track based upon its Spotify ID

            :param track_id: a track URI, URL or ID
        """
        trid = self._get_id("track", track_id)
        return self._get("audio-analysis/" + trid)

    def audio_features(self, tracks: list = []):
        """ Get audio features for one or multiple tracks based upon their Spotify IDs

            :param tracks: a list of track URIs, URLs or IDs, maximum: 100 ids
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

    def current_playback(self, market: str = None, additional_types: str = None):
        """ Get information about user's current playback.

            :param market: an ISO 3166-1 alpha-2 country code.
            :param additional_types: `episode` to get podcast track information
        """
        return self._get("me/player", market=market, additional_types=additional_types)

    def currently_playing(self, market: str = None, additional_types: str = None):
        """ Get user's currently playing track.

            :param market: an ISO 3166-1 alpha-2 country code.
            :param additional_types: `episode` to get podcast track information
        """
        return self._get("me/player/currently-playing", market=market,
                         additional_types=additional_types)

    def transfer_playback(self, device_id: str, force_play: bool = True):
        """ Transfer playback to another device.
            Note that the API accepts a list of device ids, but only
            actually supports one.

            :param device_id: transfer playback to this device
            :param force_play: true: after transfer, play. false:
                               keep current state.
        """
        data = {"device_ids": [device_id], "play": force_play}
        return self._put("me/player", payload=data)

    def start_playback(
        self, device_id: str = None, context_uri: str = None, uris: list = None, offset: object = None, position_ms: int = None
    ):
        """ Start or resume user's playback.

            Provide a `context_uri` to start playback or an album,
            artist, or playlist.

            Provide a `uris` list to start playback of one or more
            tracks.

            Provide `offset` as {"position": <int>} or {"uri": "<track uri>"}
            to start playback at a particular offset.

            :param device_id: device target for playback
            :param context_uri: spotify context uri to play
            :param uris: spotify track uris
            :param offset: offset into context by index or track
            :param position_ms: (optional) indicates from what position to start playback.
                            Must be a positive number. Passing in a position that is
                            greater than the length of the track will cause the player to
                            start playing the next song.
        """
        if context_uri is not None and uris is not None:
            logger.warning("Specify either context uri or uris, not both")
            return
        if uris is not None and not isinstance(uris, list):
            logger.warning("URIs must be a list")
            return
        data = {}
        if context_uri is not None:
            data["context_uri"] = context_uri
        if uris is not None:
            data["uris"] = uris
        if offset is not None:
            data["offset"] = offset
        if position_ms is not None:
            data["position_ms"] = position_ms
        return self._put(
            self._append_device_id("me/player/play", device_id), payload=data
        )

    def pause_playback(self, device_id: str = None):
        """ Pause user's playback.

            :param device_id: device target for playback
        """
        return self._put(self._append_device_id("me/player/pause", device_id))

    def next_track(self, device_id: str = None):
        """ Skip user's playback to next track.

            :param device_id: device target for playback
        """
        return self._post(self._append_device_id("me/player/next", device_id))

    def previous_track(self, device_id: str = None):
        """ Skip user's playback to previous track.

            :param device_id: device target for playback
        """
        return self._post(
            self._append_device_id("me/player/previous", device_id)
        )

    def seek_track(self, position_ms: int, device_id: str = None):
        """ Seek to position in current track.

            :param position_ms: position in milliseconds to seek to
            :param device_id: device target for playback
        """
        if not isinstance(position_ms, int):
            logger.warning("Position_ms must be an integer")
            return
        return self._put(
            self._append_device_id(
                "me/player/seek?position_ms=%s" % position_ms, device_id
            )
        )

    def repeat(self, state: str, device_id: str = None):
        """ Set repeat mode for playback.

            :param state: `track`, `context`, or `off`
            :param device_id: device target for playback
        """
        if state not in ["track", "context", "off"]:
            logger.warning("Invalid state")
            return
        self._put(
            self._append_device_id(
                "me/player/repeat?state=%s" % state, device_id
            )
        )

    def volume(self, volume_percent: int, device_id: str = None):
        """ Set playback volume.

            :param volume_percent: volume between 0 and 100
            :param device_id: device target for playback
        """
        if not isinstance(volume_percent, int):
            logger.warning("Volume must be an integer")
            return
        if volume_percent < 0 or volume_percent > 100:
            logger.warning("Volume must be between 0 and 100, inclusive")
            return
        self._put(
            self._append_device_id(
                "me/player/volume?volume_percent=%s" % volume_percent,
                device_id,
            )
        )

    def shuffle(self, state: str, device_id: str = None):
        """ Toggle playback shuffling.

            :param state: true or false
            :param device_id: device target for playback
        """
        if not isinstance(state, bool):
            logger.warning("state must be a boolean")
            return
        state = str(state).lower()
        self._put(
            self._append_device_id(
                "me/player/shuffle?state=%s" % state, device_id
            )
        )

    def add_to_queue(self, uri: str, device_id: str = None):
        """ Adds a song to the end of a user's queue

            If device A is currently playing music and you try to add to the queue
            and pass in the id for device B, you will get a
            'Player command failed: Restriction violated' error
            I therefore reccomend leaving device_id as None so that the active device is targeted

            :param uri: song uri, id, or url
            :param device_id:
                the id of a Spotify device.
                If None, then the active device is used.

        """

        uri = self._get_uri("track", uri)

        endpoint = "me/player/queue?uri=%s" % uri

        if device_id is not None:
            endpoint += "&device_id=%s" % device_id

        return self._post(endpoint)

    def available_markets(self):
        """ Get the list of markets where Spotify is available.
            Returns a list of the countries in which Spotify is available, identified by their
            ISO 3166-1 alpha-2 country code with additional country codes for special territories.
        """
        return self._get("markets")

    def _append_device_id(self, path, device_id):
        """ Append device ID to API path.

            :param device_id: device id to append
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
                logger.warning('Expected id of type %s but found type %s %s',
                               type, fields[-2], id)
            return fields[-1].split("?")[0]
        fields = id.split("/")
        if len(fields) >= 3:
            itype = fields[-2]
            if type != itype:
                logger.warning('Expected id of type %s but found type %s %s',
                               type, itype, id)
            return fields[-1].split("?")[0]
        return id

    def _get_uri(self, type, id):
        if self._is_uri(id):
            return id
        else:
            return "spotify:" + type + ":" + self._get_id(type, id)

    def _is_uri(self, uri: str):
        return uri.startswith("spotify:") and len(uri.split(':')) == 3

    def _search_multiple_markets(self, q, limit, offset, type, markets: list, total):
        if total and limit > total:
            limit = total
            warnings.warn(
                "limit was auto-adjusted to equal {} as it must not be higher than total".format(
                    total),
                UserWarning,
            )

        results = {}
        first_type = type.split(",")[0] + 's'
        count = 0

        for country in markets:
            result = self._get(
                "search", q=q, limit=limit, offset=offset, type=type, market=country
            )
            results[country] = result

            count += len(result[first_type]['items'])
            if total and count >= total:
                break
            if total and limit > total - count:
                # when approaching `total` results, adjust `limit` to not request more
                # items than needed
                limit = total - count

        return results

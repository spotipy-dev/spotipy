""" A simple and thin Python library for the Spotify Web API """

__all__ = ["Spotify", "SpotifyException"]

import json
import logging
import re
import warnings
from collections import defaultdict

import requests

from spotipy.exceptions import SpotifyException
from spotipy.util import Retry

logger = logging.getLogger(__name__)


class Spotify:
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

    # Spotify URI scheme defined in [1], and the ID format as base-62 in [2].
    #
    # Unfortunately the IANA specification is out of date and doesn't include the new types
    # show and episode. Additionally, for the user URI, it does not specify which characters
    # are valid for usernames, so the assumption is alphanumeric which coincidentally are also
    # the same ones base-62 uses.
    # In limited manual exploration this seems to hold true, as newly accounts are assigned an
    # identifier that looks like the base-62 of all other IDs, but some older accounts only have
    # numbers and even older ones seemed to have been allowed to freely pick this name.
    #
    # [1] https://www.iana.org/assignments/uri-schemes/prov/spotify
    # [2] https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    _regex_spotify_uri = r'^spotify:(?:(?P<type>track|artist|album|playlist|show|episode|audiobook):(?P<id>[0-9A-Za-z]+)|user:(?P<username>[0-9A-Za-z]+):playlist:(?P<playlistid>[0-9A-Za-z]+))$'  # noqa: E501

    # Spotify URLs are defined at [1]. The assumption is made that they are all
    # pointing to open.spotify.com, so a regex is used to parse them as well,
    # instead of a more complex URL parsing function.
    # Spotify recently added "/intl-<countrycode>" to their links. This change is undocumented.
    # There is an assumption that the country code uses the ISO 3166-1 alpha-2 standard [2],
    # but this has not been confirmed yet. Spotipy has no use for this, so it gets ignored.
    #
    # [1] https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    # [2] https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    _regex_spotify_url = r'^(http[s]?:\/\/)?open.spotify.com\/(intl-\w\w\/)?(?P<type>track|artist|album|playlist|show|episode|user|audiobook)\/(?P<id>[0-9A-Za-z]+)(\?.*)?$'  # noqa: E501

    _regex_base62 = r'^[0-9A-Za-z]+$'

    def __init__(
            self,
            access_token=None,
            auth_manager=None,
            requests_session=True,
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

        :param access_token: An access token (optional). If not None, then this parameter
            will override the auth_manager parameter. Prefer `auth_manager` over this parameter
            because otherwise you cannot refresh the `access_token`.
        :param auth_manager: SpotifyOauth, SpotifyClientCredentials, or SpotifyPKCE object
        :param requests_session: A Requests session object or a true value to create one.
            A false value disables sessions. It should generally be a good idea to keep
            sessions enabled for performance reasons (connection pooling).
        :param proxies: Definition of proxies (optional).
            See Requests doc https://2.python-requests.org/en/master/user/advanced/#proxies
        :param requests_timeout: Tell Requests to stop waiting for a response after a given
            number of seconds
        :param status_forcelist: Tell requests what type of status codes retries should occur on
        :param retries: Total number of retries to allow
        :param status_retries: Number of times to retry on bad status codes
        :param backoff_factor: A backoff factor to apply between attempts after the second try
            See urllib3 https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
        :param language: The language parameter advertises what language the user prefers to see.
            See ISO-639-1 language code: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        """
        if access_token is not None and auth_manager is not None:
            warnings.warn(
                "Either `access_token` or `auth_manager` should be provided, "
                "not both. `auth_manager` will be ignored.",
                UserWarning
            )

        self.prefix = "https://api.spotify.com/v1/"
        self.access_token = access_token
        self.auth_manager = auth_manager
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.status_forcelist = status_forcelist or self.default_retry_codes
        self.retries = retries
        self.status_retries = status_retries
        self.backoff_factor = backoff_factor
        self.language = language

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        elif requests_session:  # Build a new session.
            self._build_session()
        else:  # Use the Requests API module as a "session".
            self._session = requests.api

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        try:
            if isinstance(self._session, requests.Session):
                self._session.close()
        except AttributeError:
            pass

    def _build_session(self):
        self._session = requests.Session()
        retry = Retry(
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
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        if not self.auth_manager:
            return {}
        try:
            token = self.auth_manager.get_access_token()
        except TypeError:
            token = self.auth_manager.get_access_token()
        return {"Authorization": f"Bearer {token}"}

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

        logger.debug(f"Sending {method} to {url} with Params: "
                     f"{args.get('params')} Headers: {headers} and Body: {args.get('data')!r}")

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

            logger.error(f"HTTP Error for {method} to {url} with Params: "
                         f"{args.get('params')} returned {response.status_code} due to {msg}")

            raise SpotifyException(
                response.status_code,
                -1,
                f"{response.url}:\n {msg}",
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
                f"{request.path_url}:\n Max Retries",
                reason=reason
            )
        except ValueError:
            results = None

        logger.debug(f'RESULTS: {results}')
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

    def next(self, result):
        """
        Returns the next result given a paged result.

        :param result: A previously returned paged result.
        :return: The next result.
        """
        return self._get(result["next"]) if result["next"] else None

    def previous(self, result):
        """
        Returns the previous result given a paged result.

        :param result: A previously returned paged result.
        :return: The previous result.
        """
        return self._get(result["previous"]) if result["previous"] else None

    def track(self, track_id, market=None):
        """
        Returns a single track given the track's ID, URI or URL.

        :param track_id: A Spotify URI, URL or ID.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The track information.
        """

        trid = self._get_id("track", track_id)
        return self._get(f"tracks/{trid}", market=market)

    def tracks(self, tracks, market=None):
        """
        Returns a list of tracks given a list of track IDs, URIs, or URLs.

        :param tracks: A list of Spotify URIs, URLs or IDs. Maximum: 50 IDs.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of tracks information.
        """

        tlist = [self._get_id("track", t) for t in tracks]
        return self._get(f"tracks/?ids={','.join(tlist)}", market=market)

    def artist(self, artist_id):
        """
        Returns a single artist given the artist's ID, URI or URL.

        :param artist_id: An artist ID, URI or URL.
        :return: The artist information.
        """

        trid = self._get_id("artist", artist_id)
        return self._get(f"artists/{trid}")

    def artists(self, artists):
        """
        Returns a list of artists given the artist IDs, URIs, or URLs.

        :param artists: A list of artist IDs, URIs or URLs.
        :return: The list of artists information.
        """

        tlist = [self._get_id("artist", a) for a in artists]
        return self._get(f"artists/?ids={','.join(tlist)}")

    def artist_albums(
        self, artist_id, album_type=None, include_groups=None, country=None, limit=20, offset=0
    ):
        """
        Get Spotify catalog information about an artist's albums.

        :param artist_id: An artist ID, URI or URL.
        :param album_type: The type of album.
        :param include_groups: The groups to include.
        :param country: An ISO 3166-1 alpha-2 country code.
        :param limit: The number of items to return.
        :param offset: The index of the first item to return.
        :return: The artist's albums information.
        """

        if album_type:
            warnings.warn(
                "You're using `artist_albums(..., album_type='...')` which will be removed in "
                "future versions. Please adjust your code accordingly by using "
                "`artist_albums(..., include_groups='...')` instead.",
                DeprecationWarning,
            )
            include_groups = include_groups or album_type

        trid = self._get_id("artist", artist_id)
        return self._get(
            f"artists/{trid}/albums",
            album_type=album_type,
            include_groups=include_groups,
            country=country,
            limit=limit,
            offset=offset,
        )

    def artist_top_tracks(self, artist_id, country="US"):
        """
        Get Spotify catalog information about an artist's top 10 tracks by country.

        :param artist_id: The artist ID, URI or URL.
        :param country: Limit the response to one particular country.
        :return: The artist's top tracks information.
        """

        trid = self._get_id("artist", artist_id)
        return self._get(f"artists/{trid}/top-tracks", country=country)

    def artist_related_artists(self, artist_id):
        """
        Get Spotify catalog information about artists similar to an identified artist.

        :param artist_id: The artist ID, URI or URL.
        :return: The related artists' information.
        """
        warnings.warn(
            "You're using `artist_related_artists(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning
        )
        trid = self._get_id("artist", artist_id)
        return self._get(f"artists/{trid}/related-artists")

    def album(self, album_id, market=None):
        """
        Returns a single album given the album's ID, URI or URL.

        :param album_id: The album ID, URI or URL.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The album information.
        """

        trid = self._get_id("album", album_id)
        if market is not None:
            return self._get(f"albums/{trid}?market={market}")
        else:
            return self._get(f"albums/{trid}")

    def album_tracks(self, album_id, limit=50, offset=0, market=None):
        """
        Get Spotify catalog information about an album's tracks.

        :param album_id: The album ID, URI or URL.
        :param limit: The number of items to return.
        :param offset: The index of the first item to return.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The album's tracks information.
        """

        trid = self._get_id("album", album_id)
        return self._get(
            f"albums/{trid}/tracks/", limit=limit, offset=offset, market=market
        )

    def albums(self, albums, market=None):
        """
        Returns a list of albums given the album IDs, URIs, or URLs.

        :param albums: A list of album IDs, URIs or URLs.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of albums information.
        """

        tlist = [self._get_id("album", a) for a in albums]
        if market is not None:
            return self._get(f"albums/?ids={','.join(tlist)}&market={market}")
        else:
            return self._get(f"albums/?ids={','.join(tlist)}")

    def show(self, show_id, market=None):
        """
        Returns a single show given the show's ID, URI or URL.

        :param show_id: The show ID, URI or URL.
        :param market: An ISO 3166-1 alpha-2 country code. The show must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The show information.
        """

        trid = self._get_id("show", show_id)
        return self._get(f"shows/{trid}", market=market)

    def shows(self, shows, market=None):
        """
        Returns a list of shows given the show IDs, URIs, or URLs.

        :param shows: A list of show IDs, URIs or URLs.
        :param market: An ISO 3166-1 alpha-2 country code. The shows must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The list of shows information.
        """

        tlist = [self._get_id("show", s) for s in shows]
        return self._get(f"shows/?ids={','.join(tlist)}", market=market)

    def show_episodes(self, show_id, limit=50, offset=0, market=None):
        """
        Get Spotify catalog information about a show's episodes.

        :param show_id: The show ID, URI or URL.
        :param limit: The number of items to return. Default: 50.
        :param offset: The index of the first item to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code. The episodes must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The show's episodes information.
        """

        trid = self._get_id("show", show_id)
        return self._get(
            f"shows/{trid}/episodes/", limit=limit, offset=offset, market=market
        )

    def episode(self, episode_id, market=None):
        """
        Returns a single episode given the episode's ID, URI or URL.

        :param episode_id: The episode ID, URI or URL.
        :param market: An ISO 3166-1 alpha-2 country code. The episode must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The episode information.
        """

        trid = self._get_id("episode", episode_id)
        return self._get(f"episodes/{trid}", market=market)

    def episodes(self, episodes, market=None):
        """
        Returns a list of episodes given the episode IDs, URIs, or URLs.

        :param episodes: A list of episode IDs, URIs or URLs.
        :param market: An ISO 3166-1 alpha-2 country code. The episodes must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The list of episodes information.
        """

        tlist = [self._get_id("episode", e) for e in episodes]
        return self._get(f"episodes/?ids={','.join(tlist)}", market=market)

    def search(self, q, limit=10, offset=0, type="track", market=None):
        """
        Searches for an item.

        :param q: The search query.
        :param limit: The number of items to return. Default: 10.
        :param offset: The index of the first item to return. Default: 0.
        :param type: The type of item to search for. Default: "track".
        :param market: An ISO 3166-1 alpha-2 country code. The item must be available in the given market.
                       If user-based authorization is in use, the user's country takes precedence.
                       If neither market nor user country are provided, the content is considered unavailable for the client.
        :return: The search results.
        """
        return self._get(
            "search", q=q, limit=limit, offset=offset, type=type, market=market
        )

    def search_markets(self, q, limit=10, offset=0, type="track", markets=None, total=None):
        """
        (Experimental) Searches multiple markets for an item.

        :param q: The search query.
        :param limit: The number of items to return per market. Default: 10.
        :param offset: The index of the first item to return per market. Default: 0.
        :param type: The type of item to search for. Default: "track".
        :param markets: A list of ISO 3166-1 alpha-2 country codes. The item must be available in the given markets.
                        If user-based authorization is in use, the user's country takes precedence.
                        If neither market nor user country are provided, the content is considered unavailable for the client.
        :param total: The total number of items to return across all markets.
        :return: The search results.
        """
        warnings.warn(
            "Searching multiple markets is an experimental feature. "
            "Please be aware that this method's inputs and outputs can change in the future.",
            UserWarning,
        )
        if not markets:
            markets = self.country_codes

        if not (isinstance(markets, (list, tuple))):
            markets = []

        warnings.warn(
            "Searching multiple markets is poorly performing.",
            UserWarning,
        )
        return self._search_multiple_markets(q, limit, offset, type, markets, total)

    def user(self, user):
        """
        Gets basic profile information about a Spotify User.

        :param user: The ID of the user.
        :return: The user's profile information.
        """
        return self._get(f"users/{user}")

    def current_user_playlists(self, limit=50, offset=0):
        """
        Get current user playlists without requiring getting their profile.

        :param limit: The number of items to return. Default: 50.
        :param offset: The index of the first item to return. Default: 0.
        :return: The current user's playlists.
        """
        return self._get("me/playlists", limit=limit, offset=offset)

    def playlist(self, playlist_id, fields=None, market=None, additional_types=("track",)):
        """
        Gets a playlist by ID.

        :param playlist_id: The ID of the playlist.
        :param fields: Which fields to return.
        :param market: An ISO 3166-1 alpha-2 country code or the string from_token.
        :param additional_types: List of item types to return. Valid types are: track and episode.
        :return: The playlist information.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(
            f"playlists/{plid}",
            fields=fields,
            market=market,
            additional_types=",".join(additional_types),
        )

    def playlist_items(
        self,
        playlist_id,
        fields=None,
        limit=100,
        offset=0,
        market=None,
        additional_types=("track", "episode")
    ):
        """
        Get full details of the tracks and episodes of a playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param fields: Which fields to return.
        :param limit: The maximum number of tracks to return. Default: 100.
        :param offset: The index of the first track to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code.
        :param additional_types: List of item types to return. Valid types are: track and episode.
        :return: The playlist's items information.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(
            f"playlists/{plid}/tracks",
            limit=limit,
            offset=offset,
            fields=fields,
            market=market,
            additional_types=",".join(additional_types),
        )

    def playlist_cover_image(self, playlist_id):
        """
        Get cover image of a playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :return: The playlist's cover image.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._get(f"playlists/{plid}/images")

    def playlist_upload_cover_image(self, playlist_id, image_b64):
        """
        Replace the image used to represent a specific playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param image_b64: Base64 encoded JPEG image data, maximum payload size is 256 KB.
        :return: The response from the API.
        """
        plid = self._get_id("playlist", playlist_id)
        return self._put(
            f"playlists/{plid}/images",
            payload=image_b64,
            content_type="image/jpeg",
        )

    def user_playlists(self, user, limit=50, offset=0):
        """
        Gets playlists of a user.

        :param user: The ID of the user.
        :param limit: The number of items to return. Default: 50.
        :param offset: The index of the first item to return. Default: 0.
        :return: The user's playlists.
        """
        return self._get(f"users/{user}/playlists", limit=limit, offset=offset)

    def user_playlist_create(self, user, name, public=True, collaborative=False, description=""):
        """
        Creates a playlist for a user.

        :param user: The ID of the user.
        :param name: The name of the playlist.
        :param public: Whether the playlist is public. Default: True.
        :param collaborative: Whether the playlist is collaborative. Default: False.
        :param description: The description of the playlist.
        :return: The created playlist information.
        """
        data = {
            "name": name,
            "public": public,
            "collaborative": collaborative,
            "description": description
        }

        return self._post(f"users/{user}/playlists", payload=data)

    def playlist_change_details(
        self,
        playlist_id,
        name=None,
        public=None,
        collaborative=None,
        description=None,
    ):
        """
        Change a playlist's details.

        :param playlist_id: The ID of the playlist.
        :param name: The new name of the playlist.
        :param public: Whether the playlist is public.
        :param collaborative: Whether the playlist is collaborative.
        :param description: The new description of the playlist.
        :return: The response from the API.
        """

        data = {}
        if isinstance(name, str):
            data["name"] = name
        if isinstance(public, bool):
            data["public"] = public
        if isinstance(collaborative, bool):
            data["collaborative"] = collaborative
        if isinstance(description, str):
            data["description"] = description
        return self._put(
            f"playlists/{self._get_id('playlist', playlist_id)}", payload=data
        )

    def current_user_unfollow_playlist(self, playlist_id):
        """
        Unfollows (deletes) a playlist for the current authenticated user.

        :param playlist_id: The ID of the playlist.
        :return: The response from the API.
        """
        return self._delete(
            f"playlists/{self._get_id('playlist', playlist_id)}/followers"
        )

    def playlist_add_items(
        self, playlist_id, items, position=None
    ):
        """
        Add one or more items to a user's playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param items: A list of item URIs, URLs or IDs.
        :param position: The position to insert the items, a zero-based index. If omitted, the items will be appended to the playlist.
        :return: The response from the API.
        """
        for item in items:
            if not self._is_uri(item) and not self._is_url(item):
                raise RuntimeError("playlist_add_items() only accepts URIs and URLs.")
        plid = self._get_id("playlist", playlist_id)
        items = [self._url_to_uri(item) if self._is_url(item) else item for item in items]
        return self._post(
            f"playlists/{plid}/tracks",
            payload=items,
            position=position,
        )

    def playlist_replace_items(self, playlist_id, items):
        """
        Replace all items in a playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param items: A list of item URIs, URLs or IDs.
        :return: The response from the API.
        """
        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in items]
        payload = {"uris": ftracks}
        return self._put(f"playlists/{plid}/tracks", payload=payload)

    def playlist_reorder_items(
        self,
        playlist_id,
        range_start,
        insert_before,
        range_length=1,
        snapshot_id=None,
    ):
        """
        Reorder a playlist's items.

        :param playlist_id: The playlist ID, URI or URL.
        :param range_start: The position of the first item to be reordered.
        :param insert_before: The position where the items should be inserted.
        :param range_length: The number of items to be reordered. Default: 1.
        :param snapshot_id: The playlist's snapshot ID.
        :return: The response from the API.
        """
        plid = self._get_id("playlist", playlist_id)
        payload = {
            "range_start": range_start,
            "range_length": range_length,
            "insert_before": insert_before,
        }
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._put(f"playlists/{plid}/tracks", payload=payload)

    def playlist_remove_all_occurrences_of_items(
        self, playlist_id, items, snapshot_id=None
    ):
        """
        Remove all occurrences of specific items from a playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param items: A list of item URIs, URLs or IDs.
        :param snapshot_id: The playlist's snapshot ID.
        :return: The response from the API.
        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = [self._get_uri("track", tid) for tid in items]
        payload = {"tracks": [{"uri": track} for track in ftracks]}
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete(f"playlists/{plid}/tracks", payload=payload)

    def playlist_remove_specific_occurrences_of_items(
        self, playlist_id, items, snapshot_id=None
    ):
        """
        Remove specific occurrences of items from a playlist.

        :param playlist_id: The playlist ID, URI or URL.
        :param items: A list of dictionaries containing item URIs, URLs or IDs and their positions.
        :param snapshot_id: The playlist's snapshot ID.
        :return: The response from the API.
        """

        plid = self._get_id("playlist", playlist_id)
        ftracks = [
            {
                "uri": self._get_uri("track", tr["uri"]),
                "positions": tr["positions"],
            }
            for tr in items
        ]
        payload = {"tracks": ftracks}
        if snapshot_id:
            payload["snapshot_id"] = snapshot_id
        return self._delete(f"playlists/{plid}/tracks", payload=payload)

    def current_user_follow_playlist(self, playlist_id, public=True):
        """
        Add the current authenticated user as a follower of a playlist.

        :param playlist_id: The ID of the playlist.
        :param public: Whether the playlist should be followed publicly. Default: True.
        :return: The response from the API.
        """
        return self._put(
            f"playlists/{playlist_id}/followers",
            payload={"public": public}
        )

    def playlist_is_following(
        self, playlist_id, user_ids
    ):
        """
        Check if one or more users are following a playlist.

        :param playlist_id: The ID of the playlist.
        :param user_ids: A list of user IDs.
        :return: A list of booleans indicating whether each user is following the playlist.
        """
        return self._get(
            f"playlists/{playlist_id}/followers/contains?ids={','.join(user_ids)}"
        )

    def me(self):
        """
        Get detailed profile information about the current user.

        :return: The current user's profile information.
        """
        return self._get("me/")

    def current_user(self):
        """
        Get detailed profile information about the current user.

        :return: The current user's profile information.
        """
        return self.me()

    def current_user_playing_track(self):
        """
        Get information about the current user's currently playing track.

        :return: The currently playing track information.
        """
        return self._get("me/player/currently-playing")

    def current_user_saved_albums(self, limit=20, offset=0, market=None):
        """
        Get a list of the albums saved in the current authorized user's library.

        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of saved albums.
        """
        return self._get("me/albums", limit=limit, offset=offset, market=market)

    def current_user_saved_albums_add(self, albums=None):
        """
        Add one or more albums to the current user's library.

        :param albums: A list of album IDs, URIs or URLs.
        :return: The response from the API.
        """

        if albums is None:
            albums = []
        alist = [self._get_id("album", a) for a in albums]
        return self._put(f"me/albums?ids={','.join(alist)}")

    def current_user_saved_albums_delete(self, albums=None):
        """
        Remove one or more albums from the current user's library.

        :param albums: A list of album IDs, URIs or URLs.
        :return: The response from the API.
        """
        if albums is None:
            albums = []
        alist = [self._get_id("album", a) for a in albums]
        return self._delete(f"me/albums/?ids={','.join(alist)}")

    def current_user_saved_albums_contains(self, albums=None):
        """
        Check if one or more albums are already saved in the current user's library.

        :param albums: A list of album IDs, URIs or URLs.
        :return: A list of booleans indicating whether each album is saved.
        """
        if albums is None:
            albums = []
        alist = [self._get_id("album", a) for a in albums]
        return self._get(f"me/albums/contains?ids={','.join(alist)}")

    def current_user_saved_tracks(self, limit=20, offset=0, market=None):
        """
        Get a list of the tracks saved in the current authorized user's library.

        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of saved tracks.
        """
        return self._get("me/tracks", limit=limit, offset=offset, market=market)

    def current_user_saved_tracks_add(self, tracks=None):
        """
        Add one or more tracks to the current user's library.

        :param tracks: A list of track IDs, URIs or URLs.
        :return: The response from the API.
        """
        tlist = [] if tracks is None else [self._get_id("track", t) for t in tracks]
        return self._put(f"me/tracks/?ids={','.join(tlist)}")

    def current_user_saved_tracks_delete(self, tracks=None):
        """
        Remove one or more tracks from the current user's library.

        :param tracks: A list of track IDs, URIs or URLs.
        :return: The response from the API.
        """
        tlist = [] if tracks is None else [self._get_id("track", t) for t in tracks]
        return self._delete(f"me/tracks/?ids={','.join(tlist)}")

    def current_user_saved_tracks_contains(self, tracks=None):
        """
        Check if one or more tracks are already saved in the current user's library.

        :param tracks: A list of track IDs, URIs or URLs.
        :return: A list of booleans indicating whether each track is saved.
        """
        tlist = [] if tracks is None else [self._get_id("track", t) for t in tracks]
        return self._get(f"me/tracks/contains?ids={','.join(tlist)}")

    def current_user_saved_episodes(self, limit=20, offset=0, market=None):
        """
        Get a list of the episodes saved in the current authorized user's library.

        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of saved episodes.
        """
        return self._get("me/episodes", limit=limit, offset=offset, market=market)

    def current_user_saved_episodes_add(self, episodes=None):
        """
        Add one or more episodes to the current user's library.

        :param episodes: A list of episode IDs, URIs or URLs.
        :return: The response from the API.
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._put(f"me/episodes/?ids={','.join(elist)}")

    def current_user_saved_episodes_delete(self, episodes=None):
        """
        Remove one or more episodes from the current user's library.

        :param episodes: A list of episode IDs, URIs or URLs.
        :return: The response from the API.
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._delete(f"me/episodes/?ids={','.join(elist)}")

    def current_user_saved_episodes_contains(self, episodes=None):
        """
        Check if one or more episodes are already saved in the current user's library.

        :param episodes: A list of episode IDs, URIs or URLs.
        :return: A list of booleans indicating whether each episode is saved.
        """
        elist = []
        if episodes is not None:
            elist = [self._get_id("episode", e) for e in episodes]
        return self._get(f"me/episodes/contains?ids={','.join(elist)}")

    def current_user_saved_shows(self, limit=20, offset=0, market=None):
        """
        Get a list of the shows saved in the current authorized user's library.

        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The list of saved shows.
        """
        return self._get("me/shows", limit=limit, offset=offset, market=market)

    def current_user_saved_shows_add(self, shows=None):
        """
        Add one or more shows to the current user's library.

        :param shows: A list of show IDs, URIs or URLs.
        :return: The response from the API.
        """
        if shows is None:
            shows = []
        slist = [self._get_id("show", s) for s in shows]
        return self._put(f"me/shows?ids={','.join(slist)}")

    def current_user_saved_shows_delete(self, shows=None):
        """
        Remove one or more shows from the current user's library.

        :param shows: A list of show IDs, URIs or URLs.
        :return: The response from the API.
        """
        if shows is None:
            shows = []
        slist = [self._get_id("show", s) for s in shows]
        return self._delete(f"me/shows/?ids={','.join(slist)}")

    def current_user_saved_shows_contains(self, shows=None):
        """
        Check if one or more shows are already saved in the current user's library.

        :param shows: A list of show IDs, URIs or URLs.
        :return: A list of booleans indicating whether each show is saved.
        """

        if shows is None:
            shows = []
        slist = [self._get_id("show", s) for s in shows]
        return self._get(f"me/shows/contains?ids={','.join(slist)}")

    def current_user_followed_artists(self, limit=20, after=None):
        """
        Get a list of the artists followed by the current authorized user.

        :param limit: The number of artists to return. Default: 20.
        :param after: The last artist ID retrieved from the previous request.
        :return: The list of followed artists.
        """
        return self._get(f"me/following?type=artist&limit={limit}&after={after}")

    def current_user_following_artists(self, ids=None):
        """
        Check if the current user is following certain artists.

        :param ids: A list of artist URIs, URLs or IDs.
        :return: A list of booleans indicating whether each artist is followed.
        """
        idlist = [self._get_id("artist", i) for i in ids] if ids is not None else []
        return self._get(
            "me/following/contains", ids=",".join(idlist), type="artist"
        )

    def current_user_following_users(self, ids=None):
        """
        Check if the current user is following certain users.

        :param ids: A list of user URIs, URLs or IDs.
        :return: A list of booleans indicating whether each user is followed.
        """
        idlist = [self._get_id("user", i) for i in ids] if ids is not None else []
        return self._get(
            "me/following/contains", ids=",".join(idlist), type="user"
        )

    def current_user_top_artists(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        """
        Get the current user's top artists.

        :param limit: The number of entities to return. Default: 20.
        :param offset: The index of the first entity to return. Default: 0.
        :param time_range: Over what time frame are the affinities computed. Valid values: short_term, medium_term, long_term.
        :return: The list of top artists.
        """
        return self._get(
            "me/top/artists", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_top_tracks(
        self, limit=20, offset=0, time_range="medium_term"
    ):
        """
        Get the current user's top tracks.

        :param limit: The number of entities to return. Default: 20.
        :param offset: The index of the first entity to return. Default: 0.
        :param time_range: Over what time frame are the affinities computed. Valid values: short_term, medium_term, long_term.
        :return: The list of top tracks.
        """
        return self._get(
            "me/top/tracks", time_range=time_range, limit=limit, offset=offset
        )

    def current_user_recently_played(self, limit=50, after=None, before=None):
        """
        Get the current user's recently played tracks.

        :param limit: The number of entities to return. Default: 50.
        :param after: Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position. Cannot be used if before is specified.
        :param before: Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position. Cannot be used if after is specified.
        :return: The list of recently played tracks.
        """
        return self._get(
            "me/player/recently-played",
            limit=limit,
            after=after,
            before=before,
        )

    def user_follow_artists(self, ids=None):
        """
        Follow one or more artists.

        :param ids: A list of artist IDs.
        :return: The response from the API.
        """
        if ids is None:
            ids = []
        return self._put(f"me/following?type=artist&ids={','.join(ids)}")

    def user_follow_users(self, ids=None):
        """
        Follow one or more users.

        :param ids: A list of user IDs.
        :return: The response from the API.
        """
        if ids is None:
            ids = []
        return self._put(f"me/following?type=user&ids={','.join(ids)}")

    def user_unfollow_artists(self, ids=None):
        """
        Unfollow one or more artists.

        :param ids: A list of artist IDs.
        :return: The response from the API.
        """
        if ids is None:
            ids = []
        return self._delete(f"me/following?type=artist&ids={','.join(ids)}")

    def user_unfollow_users(self, ids=None):
        """
        Unfollow one or more users.

        :param ids: A list of user IDs.
        :return: The response from the API.
        """
        if ids is None:
            ids = []
        return self._delete(f"me/following?type=user&ids={','.join(ids)}")

    def featured_playlists(
        self, locale=None, country=None, timestamp=None, limit=20, offset=0
    ):
        """
         Get a list of Spotify featured playlists.

         :param locale: The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore.
         :param country: An ISO 3166-1 alpha-2 country code.
         :param timestamp: A timestamp in ISO 8601 format.
         :param limit: The number of items to return. Default: 20.
         :param offset: The index of the first item to return. Default: 0.
         :return: The list of featured playlists.
         """
        warnings.warn(
            "You're using `featured_playlists(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )
        return self._get(
            "browse/featured-playlists",
            locale=locale,
            country=country,
            timestamp=timestamp,
            limit=limit,
            offset=offset,
        )

    def new_releases(self, country=None, limit=20, offset=0):
        """
        Get a list of new album releases featured in Spotify.

        :param country: An ISO 3166-1 alpha-2 country code.
        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :return: The list of new releases.
        """
        return self._get(
            "browse/new-releases", country=country, limit=limit, offset=offset
        )

    def category(self, category_id, country=None, locale=None):
        """
        Get a single category used to tag items in Spotify (on, for example, the Spotify player’s “Browse” tab).

        :param category_id: The Spotify category ID.
        :param country: An ISO 3166-1 alpha-2 country code.
        :param locale: The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore.
        :return: The category information.
        """
        return self._get(
            f"browse/categories/{category_id}", country=country, locale=locale
        )

    def categories(self, country=None, locale=None, limit=20, offset=0):
        """
        Get a list of categories used to tag items in Spotify (on, for example, the Spotify player’s “Browse” tab).

        :param country: An ISO 3166-1 alpha-2 country code.
        :param locale: The desired language, consisting of an ISO 639-1 language code and an ISO 3166-1 alpha-2 country code, joined by an underscore.
        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :return: The list of categories.
        """
        return self._get(
            "browse/categories",
            country=country,
            locale=locale,
            limit=limit,
            offset=offset,
        )

    def category_playlists(
        self, category_id=None, country=None, limit=20, offset=0
    ):
        """
        Get a list of Spotify playlists tagged with a particular category.

        :param category_id: The Spotify category ID.
        :param country: An ISO 3166-1 alpha-2 country code.
        :param limit: The number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :return: The list of playlists.
        """
        warnings.warn(
            "You're using `category_playlists(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )
        return self._get(
            f"browse/categories/{category_id}/playlists",
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
        """
        Get a list of recommended tracks based on the given seed artists, genres, and tracks.

        :param seed_artists: A list of Spotify IDs for seed artists.
        :param seed_genres: A list of seed genres.
        :param seed_tracks: A list of Spotify IDs for seed tracks.
        :param limit: The number of items to return. Default: 20.
        :param country: An ISO 3166-1 alpha-2 country code.
        :param kwargs: Additional parameters for recommendations.
        :return: The list of recommended tracks.
        """
        warnings.warn(
            "You're using `recommendations(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )

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
        """
        Get a list of available genres seed parameter values for recommendations.

        :return: The list of available genre seeds.
        """
        warnings.warn(
            "You're using `recommendation_genre_seeds(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )
        """ Get a list of genres available for the recommendations function.
        """
        return self._get("recommendations/available-genre-seeds")

    def audio_analysis(self, track_id):
        """
        Get audio analysis for a track based upon its Spotify ID.

        :param track_id: A Spotify URI, URL or ID.
        :return: The audio analysis information.
        """
        warnings.warn(
            "You're using `audio_analysis(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )
        trid = self._get_id("track", track_id)
        return self._get(f"audio-analysis/{trid}")

    def audio_features(self, tracks=None):
        """
        Get audio features for one or multiple tracks based upon their Spotify IDs.

        :param tracks: A list of track IDs, URIs or URLs.
        :return: The audio features information.
        """
        warnings.warn(
            "You're using `audio_features(...)`, "
            "which is marked as deprecated by Spotify.",
            DeprecationWarning,
        )

        if tracks is None:
            tracks = []

        if isinstance(tracks, str):
            trackid = self._get_id("track", tracks)
            results = self._get(f"audio-features/?ids={trackid}")
        else:
            tlist = [self._get_id("track", t) for t in tracks]
            results = self._get(f"audio-features/?ids={','.join(tlist)}")
        # the response has changed, look for the new style first, and if
        # it's not there, fallback on the old style
        if "audio_features" in results:
            return results["audio_features"]
        else:
            return results

    def devices(self):
        """
        Get a list of user's available devices.

        :return: The list of available devices.
        """
        return self._get("me/player/devices")

    def current_playback(self, market=None, additional_types=None):
        """
        Get information about user's current playback.

        :param market: An ISO 3166-1 alpha-2 country code.
        :param additional_types: List of item types to return. Valid types are: track and episode.
        :return: The current playback information.
        """
        return self._get("me/player", market=market, additional_types=additional_types)

    def currently_playing(self, market=None, additional_types=None):
        """
        Get user's currently playing track.

        :param market: An ISO 3166-1 alpha-2 country code.
        :param additional_types: List of item types to return. Valid types are: track and episode.
        :return: The currently playing track information.
        """
        return self._get("me/player/currently-playing", market=market,
                         additional_types=additional_types)

    def transfer_playback(self, device_id, force_play=True):
        """
        Transfer playback to another device.

        :param device_id: The ID of the device.
        :param force_play: Whether to start playback on the new device. Default: True.
        :return: The response from the API.
        """
        data = {"device_ids": [device_id], "play": force_play}
        return self._put("me/player", payload=data)

    def start_playback(
        self, device_id=None, context_uri=None, uris=None, offset=None, position_ms=None
    ):
        """
        Start or resume user's playback.

        :param device_id: The ID of the device.
        :param context_uri: Spotify context URI to play.
        :param uris: List of Spotify track URIs.
        :param offset: Offset into context by index or track.
        :param position_ms: Indicates from what position to start playback.
        :return: The response from the API.
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

    def pause_playback(self, device_id=None):
        """
        Pause user's playback.

        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        return self._put(self._append_device_id("me/player/pause", device_id))

    def next_track(self, device_id=None):
        """
        Skip user's playback to next track.

        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        return self._post(self._append_device_id("me/player/next", device_id))

    def previous_track(self, device_id=None):
        """
        Skip user's playback to previous track.

        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        return self._post(
            self._append_device_id("me/player/previous", device_id)
        )

    def seek_track(self, position_ms, device_id=None):
        """
        Seek to position in current track.

        :param position_ms: Position in milliseconds to seek to.
        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        if not isinstance(position_ms, int):
            logger.warning("Position_ms must be an integer")
            return
        return self._put(
            self._append_device_id(
                f"me/player/seek?position_ms={position_ms}", device_id
            )
        )

    def repeat(self, state, device_id=None):
        """
        Set repeat mode for playback.

        :param state: `track`, `context`, or `off`.
        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        if state not in ["track", "context", "off"]:
            logger.warning("Invalid state")
            return
        self._put(self._append_device_id(f"me/player/repeat?state={state}", device_id))

    def volume(self, volume_percent, device_id=None):
        """
        Set playback volume.

        :param volume_percent: Volume between 0 and 100.
        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        if not isinstance(volume_percent, int):
            logger.warning("Volume must be an integer")
            return
        if volume_percent < 0 or volume_percent > 100:
            logger.warning("Volume must be between 0 and 100, inclusive")
            return
        self._put(
            self._append_device_id(
                f"me/player/volume?volume_percent={volume_percent}", device_id
            )
        )

    def shuffle(self, state, device_id=None):
        """
        Toggle playback shuffling.

        :param state: A boolean indicating whether to enable or disable shuffling.
        :param device_id: The ID of the device.
        :return: The response from the API.
        """
        if not isinstance(state, bool):
            logger.warning("state must be a boolean")
            return
        state = str(state).lower()
        self._put(
            self._append_device_id(f"me/player/shuffle?state={state}", device_id)
        )

    def queue(self):
        """
        Get the current user's queue.

        :return: The current user's queue.
        """
        return self._get("me/player/queue")

    def add_to_queue(self, uri, device_id=None):
        """
        Add a song to the end of a user's queue.

        If device A is currently playing music, and you try to add to the queue
        and pass in the ID for device B, you will get a 'Player command failed: Restriction violated' error.
        It is recommended to leave device_id as None so that the active device is targeted.

        :param uri: The song URI, ID, or URL.
        :param device_id: The ID of a Spotify device. If None, the active device is used.
        :return: The response from the API.
        """

        uri = self._get_uri("track", uri)

        endpoint = f"me/player/queue?uri={uri}"

        if device_id is not None:
            endpoint += f"&device_id={device_id}"

        return self._post(endpoint)

    def available_markets(self):
        """
        Get the list of markets where Spotify is available.

        Returns a list of the countries in which Spotify is available, identified by their
        ISO 3166-1 alpha-2 country code with additional country codes for special territories.

        :return: The list of available markets.
        """
        return self._get("markets")

    def _append_device_id(self, path, device_id):
        if device_id:
            path += f"&device_id={device_id}" if "?" in path else f"?device_id={device_id}"
        return path

    def _get_id(self, type, id):
        uri_match = re.search(Spotify._regex_spotify_uri, id)
        if uri_match is not None:
            uri_match_groups = uri_match.groupdict()
            if uri_match_groups['type'] != type:
                # TODO change to a ValueError in v3
                raise SpotifyException(400, -1, "Unexpected Spotify URI type.")
            return uri_match_groups['id']

        url_match = re.search(Spotify._regex_spotify_url, id)
        if url_match is not None:
            url_match_groups = url_match.groupdict()
            if url_match_groups['type'] != type:
                raise SpotifyException(400, -1, "Unexpected Spotify URL type.")
            # TODO change to a ValueError in v3
            return url_match_groups['id']

        # Raw identifiers might be passed, ensure they are also base-62
        if re.search(Spotify._regex_base62, id) is not None:
            return id

        # TODO change to a ValueError in v3
        raise SpotifyException(400, -1, "Unsupported URL / URI.")

    def _get_uri(self, type, id):
        return id if self._is_uri(id) else f"spotify:{type}:{self._get_id(type, id)}"

    def _is_uri(self, uri):
        return re.search(Spotify._regex_spotify_uri, uri) is not None

    def _is_url(self, url):
        return url.startswith("http")

    def _url_to_uri(self, url):
        splitted = url.split("/")
        return "spotify:" + splitted[-2] + ":" + splitted[-1]

    def _search_multiple_markets(self, q, limit, offset, type, markets, total):
        if total and limit > total:
            limit = total
            warnings.warn(f"limit was auto-adjusted to equal {total} "
                          f"as it must not be higher than total",
                          UserWarning)

        results = defaultdict(dict)
        item_types = [f"{item_type}s" for item_type in type.split(",")]
        count = 0

        for country in markets:
            result = self._get(
                "search", q=q, limit=limit, offset=offset, type=type, market=country
            )
            for item_type in item_types:
                results[country][item_type] = result[item_type]

                # Truncate the items list to the current limit
                if len(results[country][item_type]['items']) > limit:
                    results[country][item_type]['items'] = \
                        results[country][item_type]['items'][:limit]

                count += len(results[country][item_type]['items'])
                if total and limit > total - count:
                    # when approaching `total` results, adjust `limit` to not request more
                    # items than needed
                    limit = total - count

            if total and count >= total:
                return results

        return results

    def get_audiobook(self, id, market=None):
        """
        Get Spotify catalog information for a single audiobook identified by its unique Spotify ID.

        :param id: The Spotify ID for the audiobook.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The audiobook information.
        """
        audiobook_id = self._get_id("audiobook", id)
        endpoint = f"audiobooks/{audiobook_id}"

        if market:
            endpoint += f'?market={market}'

        return self._get(endpoint)

    def get_audiobooks(self, ids, market=None):
        """
        Get Spotify catalog information for multiple audiobooks based on their Spotify IDs.

        :param ids: A list of Spotify IDs for the audiobooks.
        :param market: An ISO 3166-1 alpha-2 country code.
        :return: The audiobooks information.
        """
        audiobook_ids = [self._get_id("audiobook", id) for id in ids]
        endpoint = f"audiobooks?ids={','.join(audiobook_ids)}"

        if market:
            endpoint += f'&market={market}'

        return self._get(endpoint)

    def get_audiobook_chapters(self, id, market=None, limit=20, offset=0):
        """
        Get Spotify catalog information about an audiobook’s chapters.

        :param id: The Spotify ID for the audiobook.
        :param market: An ISO 3166-1 alpha-2 country code.
        :param limit: The maximum number of items to return. Default: 20.
        :param offset: The index of the first item to return. Default: 0.
        :return: The audiobook's chapters information.
        """
        audiobook_id = self._get_id("audiobook", id)
        endpoint = f"audiobooks/{audiobook_id}/chapters?limit={limit}&offset={offset}"

        if market:
            endpoint += f'&market={market}'

        return self._get(endpoint)

# -*- coding: utf-8 -*-

""" Shows a user's playlists. This needs to be authenticated via OAuth) """


__all__ = ["CLIENT_CREDS_ENV_VARS", "prompt_for_user_token"]

import logging
import os
import warnings

import spotipy

LOGGER = logging.getLogger(__name__)

CLIENT_CREDS_ENV_VARS = {
    "client_id": "SPOTIPY_CLIENT_ID",
    "client_secret": "SPOTIPY_CLIENT_SECRET",
    "client_username": "SPOTIPY_CLIENT_USERNAME",
    "redirect_uri": "SPOTIPY_REDIRECT_URI",
}


def prompt_for_user_token(
    username=None,
    scope=None,
    client_id=None,
    client_secret=None,
    redirect_uri=None,
    cache_path=None,
    oauth_manager=None,
    show_dialog=False
):
    warnings.warn(
        "'prompt_for_user_token' is deprecated."
        "Use the following instead: "
        "    auth_manager=SpotifyOAuth(scope=scope)"
        "    spotipy.Spotify(auth_manager=auth_manager)",
        DeprecationWarning
    )
    """Prompt the user to login if necessary and return a user token.

        Prompts the user to login if necessary and returns the user token
        suitable for use with the `spotipy.Spotify` constructor.

        Args:
            username: The Spotify username. (optional)
            scope: The desired scope of the request. (optional)
            client_id: The client ID of your app. (required)
            client_secret: The client secret of your app. (required)
            redirect_uri: The redirect URI of your app. (required)
            cache_path: Path to location to save tokens. (required)
            oauth_manager: OAuth manager object. (optional)
            show_dialog: If True, a login prompt always shows; defaults to False. (optional)

        Returns:
            A token suitable for use with the `spotipy.Spotify` constructor.
            None: If no valid token is found.

        Raises:
            SpotifyException: If no credentials are set.
    """

    if not oauth_manager:
        if not client_id:
            client_id = os.getenv("SPOTIPY_CLIENT_ID")

        if not client_secret:
            client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

        if not redirect_uri:
            redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

        if not client_id:
            LOGGER.warning(
                """
                You need to set your Spotify API credentials.
                You can do this by setting environment variables like so:

                export SPOTIPY_CLIENT_ID='your-spotify-client-id'
                export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
                export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

                Get your credentials at
                    https://developer.spotify.com/my-applications
            """
            )
            raise spotipy.SpotifyException(550, -1, "no credentials set")

    sp_oauth = oauth_manager or spotipy.SpotifyOAuth(
        client_id,
        client_secret,
        redirect_uri,
        scope=scope,
        cache_path=cache_path,
        username=username,
        show_dialog=show_dialog
    )

    # try to get a valid token for this user, from the cache,
    # if not in the cache, then create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())

    if not token_info:
        code = sp_oauth.get_auth_response()
        token = sp_oauth.get_access_token(code, as_dict=False)
    else:
        return token_info["access_token"]

    # Auth'ed API request
    if token:
        return token
    else:
        return None


def get_host_port(netloc):
    """Split the network location string into host and port.

    Args:
        netloc: A string representing the network location.

    Returns:
        A tuple where the first element is the host as a string, and the second element
        is the port as an integer.
        None if no port is specified.
    """
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        port = int(port)
    else:
        host = netloc
        port = None

    return host, port


def normalize_scope(scope):
    """Normalize the scope to verify that it is a list or tuple.

    If the input is a string, the function splits the string by commas to
    create a list of scopes.
    If the input is already a list or tuple. it is used directly.

    Args:
        scope: A string representing scopes separated by commas, or a list/tuple of scopes.

    Returns:
        A string of sorted scopes separated by spaces if input is valid, otherwise None.

    Raises:
        Exception: If the scope is not a string, list, or tuple.
        The scope value must be a list of scopes or a string of scopes
        separated by commas.
    """
    if scope:
        if isinstance(scope, str):
            scopes = scope.split(',')
        elif isinstance(scope, list) or isinstance(scope, tuple):
            scopes = scope
        else:
            raise Exception(
                "Unsupported scope value, please either provide a list of scopes, "
                "or a string of scopes separated by commas"
            )
        return " ".join(sorted(scopes))
    else:
        return None

# -*- coding: utf-8 -*-

""" Shows a user's playlists (need to be authenticated via oauth) """

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
    """ prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify
        constructor

        Parameters:

         - username - the Spotify username (optional)
         - scope - the desired scope of the request (optional)
         - client_id - the client id of your app (required)
         - client_secret - the client secret of your app (required)
         - redirect_uri - the redirect URI of your app (required)
         - cache_path - path to location to save tokens (optional)
         - oauth_manager - Oauth manager object (optional)
         - show_dialog - If true, a login prompt always shows (optional, defaults to False)

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
    # if not in the cache, the create a new (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

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
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        port = int(port)
    else:
        host = netloc
        port = None

    return host, port

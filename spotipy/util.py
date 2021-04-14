from __future__ import annotations

""" Shows a user's playlists. This needs to be authenticated via OAuth. """

__all__ = ["CLIENT_CREDS_ENV_VARS"]

import logging
import os
import warnings
from types import TracebackType

import spotipy

import urllib3

LOGGER = logging.getLogger(__name__)

CLIENT_CREDS_ENV_VARS = {
    "client_id": "SPOTIPY_CLIENT_ID",
    "client_secret": "SPOTIPY_CLIENT_SECRET",
    "client_username": "SPOTIPY_CLIENT_USERNAME",
    "redirect_uri": "SPOTIPY_REDIRECT_URI",
}


def get_host_port(netloc):
    """ Split the network location string into host and port and returns a tuple
        where the host is a string and the the port is an integer.

        Parameters:
            - netloc - a string representing the network location.
    """
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        port = int(port)
    else:
        host = netloc
        port = None

    return host, port

# -*- coding: utf-8 -*-

""" Shows a user's playlists (need to be authenticated via oauth) """

__all__ = ["CLIENT_CREDS_ENV_VARS"]

import logging
from typing import Dict, Optional, Tuple

LOGGER = logging.getLogger(__name__)

CLIENT_CREDS_ENV_VARS: Dict[str, str] = {
    "client_id": "SPOTIPY_CLIENT_ID",
    "client_secret": "SPOTIPY_CLIENT_SECRET",
    "client_username": "SPOTIPY_CLIENT_USERNAME",
    "redirect_uri": "SPOTIPY_REDIRECT_URI",
}


def get_host_port(netloc: str) -> Tuple[str, Optional[int]]:
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        port = int(port)
    else:
        host = netloc
        port = None

    return host, port

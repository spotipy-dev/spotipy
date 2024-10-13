from __future__ import annotations

from spotipy.scope import Scope

""" Shows a user's playlists. This needs to be authenticated via OAuth. """

__all__ = ["CLIENT_CREDS_ENV_VARS", "get_host_port", "normalize_scope", "Retry"]

import logging
from types import TracebackType
from collections.abc import Iterable

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


def normalize_scope(scope):
    """Normalize the scope to verify that it is a list or tuple. A string
    input will split the string by commas to create a list of scopes.
    A list or tuple input is used directly.

    Parameters:
        - scope - a string representing scopes separated by commas,
                  or a list/tuple of scopes.
    """
    if scope:
        if isinstance(scope, str):
            scopes = scope.split(',')

        elif isinstance(scope, Iterable):
            if all(isinstance(s, Scope) for s in scope):
                return Scope.make_string(scope)
            scopes = scope
        else:
            raise TypeError(
                "Unsupported scope value, please either provide a list of scopes, "
                "or a string of scopes separated by commas."
            )
        return " ".join(sorted(scopes))
    else:
        return None


class Retry(urllib3.Retry):
    """
    Custom class for printing a warning when a rate/request limit is reached.
    """
    def increment(
            self,
            method: str | None = None,
            url: str | None = None,
            response: urllib3.BaseHTTPResponse | None = None,
            error: Exception | None = None,
            _pool: urllib3.connectionpool.ConnectionPool | None = None,
            _stacktrace: TracebackType | None = None,
    ) -> urllib3.Retry:
        if response:
            retry_header = response.headers.get("Retry-After")
            if self.is_retry(method, response.status, bool(retry_header)):
                logging.warning("Your application has reached a rate/request limit. "
                                f"Retry will occur after: {retry_header}")
        return super().increment(method,
                                 url,
                                 response=response,
                                 error=error,
                                 _pool=_pool,
                                 _stacktrace=_stacktrace)

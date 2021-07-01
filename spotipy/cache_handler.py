# -*- coding: utf-8 -*-

__all__ = ['CacheHandler', 'CacheFileHandler', 'MemoryCacheHandler', 'TokenInfo']

import errno
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from spotipy.util import CLIENT_CREDS_ENV_VARS

logger = logging.getLogger(__name__)

TokenInfo = TypedDict("TokenInfo", {
    "access_token": str,
    "token_type": str,
    "scope": str,
    "expires_in": int,
    "refresh_token": str,
    "expires_at": int
})


class CacheHandler(ABC):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Clients are expected to subclass this class and override the
    get_cached_token and save_token_to_cache methods with the same
    type signatures of this class.
    """

    @abstractmethod
    def get_cached_token(self) -> Optional[TokenInfo]:
        """
        Get and return a token_info dictionary object.
        """

    @abstractmethod
    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """
        Save a token_info dictionary object to the cache and return None.
        """


class CacheFileHandler(CacheHandler):
    """
    Handles reading and writing cached Spotify authorization tokens
    as json files on disk.
    """

    def __init__(self,
                 cache_path: Optional[str] = None,
                 username: Optional[str] = None):
        """
        Parameters:
             * cache_path: May be supplied, will otherwise be generated
                           (takes precedence over `username`)
             * username: May be supplied or set as environment variable
                         (will set `cache_path` to `.cache-{username}`)
        """

        if cache_path:
            self.cache_path = cache_path
        else:
            cache_path = ".cache"
            username = (username or os.getenv(CLIENT_CREDS_ENV_VARS["client_username"]))
            if username:
                cache_path += "-" + str(username)
            self.cache_path = cache_path

    def get_cached_token(self) -> Optional[TokenInfo]:
        token_info = None

        try:
            f = open(self.cache_path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)

        except IOError as error:
            if error.errno == errno.ENOENT:
                logger.debug("cache does not exist at: %s", self.cache_path)
            else:
                logger.warning("Couldn't read cache at: %s", self.cache_path)

        return token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        try:
            f = open(self.cache_path, "w")
            f.write(json.dumps(token_info))
            f.close()
        except IOError:
            logger.warning('Couldn\'t write token to cache at: %s',
                           self.cache_path)


class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info: Optional[TokenInfo] = None):
        """
        Parameters:
            * token_info: The token info to store in memory. Can be None.
        """
        self.token_info = token_info

    def get_cached_token(self) -> Optional[TokenInfo]:
        return self.token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        self.token_info = token_info

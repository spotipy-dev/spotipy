from __future__ import annotations

import errno
import json
import logging
import os
from abc import ABC, abstractmethod
from json import JSONEncoder
from typing import TypedDict

from redis import RedisError

from .util import CLIENT_CREDS_ENV_VARS

__all__ = [
    "CacheHandler",
    "CacheFileHandler",
    "DjangoSessionCacheHandler",
    "FlaskSessionCacheHandler",
    "MemoryCacheHandler",
    "RedisCacheHandler",
    "MemcacheCacheHandler",
]

logger = logging.getLogger(__name__)


class TokenInfo(TypedDict):
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    refresh_token: str
    expires_at: int


class CacheHandler(ABC):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Custom extensions of this class must implement get_cached_token
    and save_token_to_cache methods with the same input and output
    structure as the CacheHandler class.
    """

    @abstractmethod
    def get_cached_token(self) -> TokenInfo | None:
        """Get and return a token_info dictionary object."""

    @abstractmethod
    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """Save a token_info dictionary object to the cache and return None."""


class CacheFileHandler(CacheHandler):
    """Read and write cached Spotify authorization tokens as json files on disk."""

    def __init__(
        self,
        cache_path: str | None = None,
        username: str | None = None,
        encoder_cls: type[JSONEncoder] | None = None,
    ) -> None:
        """
        Initialize CacheFileHandler instance.

        :param cache_path: (Optional) Path to cache. (Will override 'username')
        :param username: (Optional) Client username. (Can also be supplied via env var.)
        :param encoder_cls: (Optional) JSON encoder class to override default.
        """
        self.encoder_cls = encoder_cls
        if cache_path:
            self.cache_path = cache_path
        else:
            cache_path = ".cache"
            username = username or os.getenv(CLIENT_CREDS_ENV_VARS["client_username"])
            if username:
                cache_path += "-" + str(username)
            self.cache_path = cache_path

    def get_cached_token(self) -> TokenInfo | None:
        """Get cached token from file."""
        token_info: TokenInfo | None = None

        try:
            with open(self.cache_path) as f:
                token_info = json.load(f)

        except OSError as error:
            if error.errno == errno.ENOENT:
                logger.debug("cache does not exist at: %s", self.cache_path)
            else:
                logger.warning("Couldn't read cache at: %s", self.cache_path)

        return token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """Save token cache to file."""
        try:
            with open(self.cache_path, "w") as f:
                json.dump(token_info, f, cls=self.encoder_cls)
        except OSError:
            logger.warning("Couldn't write token to cache at: %s", self.cache_path)


class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info=None):
        """
        Parameters:
            * token_info: The token info to store in memory. Can be None.
        """
        self.token_info = token_info

    def get_cached_token(self):
        return self.token_info

    def save_token_to_cache(self, token_info):
        self.token_info = token_info


class DjangoSessionCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the session framework
    provided by Django.

    Read more at https://docs.djangoproject.com/en/3.2/topics/http/sessions/
    """

    def __init__(self, request):
        """
        Parameters:
            * request: HttpRequest object provided by Django for every
            incoming request
        """
        self.request = request

    def get_cached_token(self):
        token_info = None
        try:
            token_info = self.request.session['token_info']
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            self.request.session['token_info'] = token_info
        except Exception as e:
            logger.warning("Error saving token to cache: " + str(e))


class FlaskSessionCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the session framework
    provided by flask.
    """

    def __init__(self, session):
        self.session = session

    def get_cached_token(self):
        token_info = None
        try:
            token_info = self.session["token_info"]
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            self.session["token_info"] = token_info
        except Exception as e:
            logger.warning("Error saving token to cache: " + str(e))


class RedisCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the Redis.
    """

    def __init__(self, redis, key=None):
        """
        Parameters:
            * redis: Redis object provided by redis-py library
            (https://github.com/redis/redis-py)
            * key: May be supplied, will otherwise be generated
                   (takes precedence over `token_info`)
        """
        self.redis = redis
        self.key = key if key else 'token_info'

    def get_cached_token(self):
        token_info = None
        try:
            token_info = self.redis.get(self.key)
            if token_info:
                return json.loads(token_info)
        except RedisError as e:
            logger.warning('Error getting token from cache: ' + str(e))

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            self.redis.set(self.key, json.dumps(token_info))
        except RedisError as e:
            logger.warning('Error saving token to cache: ' + str(e))


class MemcacheCacheHandler(CacheHandler):
    """A Cache handler that stores the token info in Memcache using the pymemcache client
    """

    def __init__(self, memcache, key=None) -> None:
        """
        Parameters:
            * memcache: memcache client object provided by pymemcache
            (https://pymemcache.readthedocs.io/en/latest/getting_started.html)
            * key: May be supplied, will otherwise be generated
                   (takes precedence over `token_info`)
        """
        self.memcache = memcache
        self.key = key if key else 'token_info'

    def get_cached_token(self):
        from pymemcache import MemcacheError
        try:
            token_info = self.memcache.get(self.key)
            if token_info:
                return json.loads(token_info.decode())
        except MemcacheError as e:
            logger.warning('Error getting token from cache' + str(e))

    def save_token_to_cache(self, token_info):
        from pymemcache import MemcacheError
        try:
            self.memcache.set(self.key, json.dumps(token_info))
        except MemcacheError as e:
            logger.warning('Error saving token to cache' + str(e))

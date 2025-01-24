from __future__ import annotations

import errno
import json
import logging
import os
from abc import ABC, abstractmethod
from json import JSONEncoder
from typing import TypedDict

import redis
import redis.client
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
    expires_in: int
    scope: str
    expires_at: int
    refresh_token: str


class CacheHandler(ABC):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Clients are expected to subclass this class and override the
    get_cached_token and save_token_to_cache methods with the same
    type signatures of this class.
    """

    @abstractmethod
    def get_cached_token(self) -> TokenInfo | None:
        """
        Get and return a token_info dictionary object.

        :return: A token_info dictionary object or None if no token is cached.
        """

    @abstractmethod
    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """
        Save a token_info dictionary object to the cache.

        :param token_info: A token_info dictionary object to be cached.
        """


class CacheFileHandler(CacheHandler):
    """
    Read and write cached Spotify authorization tokens as json files on disk.
    """

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
                cache_path += f"-{username}"
            self.cache_path = cache_path

    def get_cached_token(self) -> TokenInfo | None:
        """
        Get cached token from file.

        :return: A token_info dictionary object or None if no token is cached.
        """
        token_info: TokenInfo | None = None

        try:
            f = open(self.cache_path)
            token_info_string = f.read()
            f.close()
            token_info = json.loads(token_info_string)

        except OSError as error:
            if error.errno == errno.ENOENT:
                logger.debug(f"cache does not exist at: {self.cache_path}")
            else:
                logger.warning(f"Couldn't read cache at: {self.cache_path}")

        return token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """
        Save token cache to file.

        :param token_info: A token_info dictionary object to be cached.
        """
        try:
            f = open(self.cache_path, "w")
            f.write(json.dumps(token_info, cls=self.encoder_cls))
            f.close()
        except OSError:
            logger.warning(f"Couldn't write token to cache at: {self.cache_path}")


class MemoryCacheHandler(CacheHandler):
    """
    Cache handler that stores the token non-persistently as an instance attribute.
    """

    def __init__(self, token_info: TokenInfo | None = None) -> None:
        """
        Initialize MemoryCacheHandler instance.

        :param token_info: Optional initial cached token.
        """
        self.token_info = token_info

    def get_cached_token(self) -> TokenInfo | None:
        """
        Retrieve the cached token from the instance.

        :return: A token_info dictionary object or None if no token is cached.
        """
        return self.token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """
        Cache the token in this instance.

        :param token_info: A token_info dictionary object to be cached.
        """
        self.token_info = token_info


class DjangoSessionCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the session framework
    provided by Django.

    Read more at https://docs.djangoproject.com/en/3.2/topics/http/sessions/
    """

    def __init__(self, request):
        """
        Initialize DjangoSessionCacheHandler instance.

        :param request: HttpRequest object provided by Django for every incoming request.
        """
        self.request = request

    def get_cached_token(self):
        """
        Retrieve the cached token from the Django session.

        :return: A token_info dictionary object or None if no token is cached.
        """
        token_info = None
        try:
            token_info = self.request.session["token_info"]
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        """
        Cache the token in the Django session.

        :param token_info: A token_info dictionary object to be cached.
        """
        try:
            self.request.session["token_info"] = token_info
        except Exception as e:
            logger.warning(f"Error saving token to cache: {e}")


class FlaskSessionCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the session framework
    provided by Flask.
    """

    def __init__(self, session):
        """
        Initialize FlaskSessionCacheHandler instance.

        :param session: Flask session object.
        """
        self.session = session

    def get_cached_token(self):
        """
        Retrieve the cached token from the Flask session.

        :return: A token_info dictionary object or None if no token is cached.
        """
        token_info = None
        try:
            token_info = self.session["token_info"]
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        """
        Cache the token in the Flask session.

        :param token_info: A token_info dictionary object to be cached.
        """
        try:
            self.session["token_info"] = token_info
        except Exception as e:
            logger.warning(f"Error saving token to cache: {e}")


class RedisCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in Redis.
    """

    def __init__(self, redis_obj: redis.client.Redis, key: str | None = None) -> None:
        """
        Initialize RedisCacheHandler instance.

        :param redis_obj: The Redis object to function as the cache.
        :param key: (Optional) The key to use to store the token in the cache.
        """
        self.redis = redis_obj
        self.key = key or "token_info"

    def get_cached_token(self) -> TokenInfo | None:
        """
        Fetch cached token from Redis.

        :return: A token_info dictionary object or None if no token is cached.
        """
        token_info = None
        try:
            token_info = self.redis.get(self.key)
            if token_info is not None:
                token_info = json.loads(token_info)
        except RedisError as e:
            logger.warning(f"Error getting token from cache: {e}")

        return token_info

    def save_token_to_cache(self, token_info: TokenInfo) -> None:
        """
        Cache token in Redis.

        :param token_info: A token_info dictionary object to be cached.
        """
        try:
            self.redis.set(self.key, json.dumps(token_info))
        except RedisError as e:
            logger.warning(f"Error saving token to cache: {e}")


class MemcacheCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in Memcache using the pymemcache client.
    """

    def __init__(self, memcache, key=None) -> None:
        """
        Initialize MemcacheCacheHandler instance.

        :param memcache: Memcache client object provided by pymemcache.
        :param key: (Optional) The key to use to store the token in the cache.
        """
        self.memcache = memcache
        self.key = key or "token_info"

    def get_cached_token(self):
        """
        Fetch cached token from Memcache.

        :return: A token_info dictionary object or None if no token is cached.
        """
        from pymemcache import MemcacheError

        try:
            token_info = self.memcache.get(self.key)
            if token_info:
                return json.loads(token_info.decode())
        except MemcacheError as e:
            logger.warning(f"Error getting token to cache: {e}")

    def save_token_to_cache(self, token_info):
        """
        Cache token in Memcache.

        :param token_info: A token_info dictionary object to be cached.
        """
        from pymemcache import MemcacheError

        try:
            self.memcache.set(self.key, json.dumps(token_info))
        except MemcacheError as e:
            logger.warning(f"Error saving token to cache: {e}")

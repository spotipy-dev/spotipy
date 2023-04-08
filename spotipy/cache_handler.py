import pathlib
__all__ = [
    'CacheHandler',
    'CacheFileHandler',
    'DjangoSessionCacheHandler',
    'FlaskSessionCacheHandler',
    'MemoryCacheHandler',
    'RedisCacheHandler']

import errno
import json
import logging
import os
from spotipy.util import CLIENT_CREDS_ENV_VARS
from abc import ABC, abstractmethod
import warnings

logger = logging.getLogger(__name__)


class CacheHandler(ABC):
    """
    An abstraction layer for handling the caching and retrieval of
    authorization tokens.

    Clients are expected to subclass this class and override the
    get_cached_token and save_token_to_cache methods with the same
    type signatures of this class.
    """

    @abstractmethod
    def get_cached_token(self):
        """
        Get and return a token_info dictionary object.
        """

    @abstractmethod
    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None.
        """


class CacheFileHandler(CacheHandler):
    """
    Handles reading and writing cached Spotify authorization tokens
    as json files on disk.
    """

    def __init__(self,
                 cache_path=None,
                 username=None):
        """
        Parameters:
             * cache_path: May be supplied, will otherwise be generated
                           (takes precedence over `username`)
             * username: May be supplied or set as environment variable
                         (will set `cache_path` to `.cache-{username}`)
        """

        if not cache_path:
            cache_path = ".cache"
            if username := (
                username or os.getenv(CLIENT_CREDS_ENV_VARS["client_username"])
            ):
                cache_path += f"-{str(username)}"
        self.cache_path = cache_path

    def get_cached_token(self):
        token_info = None

        try:
            token_info_string = pathlib.Path(self.cache_path).read_text()
            token_info = json.loads(token_info_string)

        except IOError as error:
            if error.errno == errno.ENOENT:
                logger.debug("cache does not exist at: %s", self.cache_path)
            else:
                logger.warning("Couldn't read cache at: %s", self.cache_path)

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            with open(self.cache_path, "w") as f:
                f.write(json.dumps(token_info))
        except IOError:
            logger.warning('Couldn\'t write token to cache at: %s',
                           self.cache_path)


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
            logger.warning(f"Error saving token to cache: {str(e)}")


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
            logger.warning(f"Error saving token to cache: {str(e)}")


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
        self.key = key or 'token_info'

        try:
            from redis import RedisError  # noqa: F401
        except ImportError:
            warnings.warn(
                'Error importing module "redis"; '
                'it is required for RedisCacheHandler',
                UserWarning
            )

    def get_cached_token(self):
        token_info = None
        from redis import RedisError

        try:
            token_info = self.redis.get(self.key)
            if token_info:
                return json.loads(token_info)
        except RedisError as e:
            logger.warning(f'Error getting token from cache: {str(e)}')

        return token_info

    def save_token_to_cache(self, token_info):
        from redis import RedisError

        try:
            self.redis.set(self.key, json.dumps(token_info))
        except RedisError as e:
            logger.warning(f'Error saving token to cache: {str(e)}')

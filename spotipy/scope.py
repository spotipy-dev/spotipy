# -*- coding: utf-8 -*-

__all__ = ["Scope"]

from enum import Enum
import re
from typing import Iterable, Set


class Scope(Enum):
    """
    The Spotify authorization scopes

    Create a Scope from a string:

    scope = Scope("playlist-modify-private")

    Create a set of scopes:

    scopes = {
        Scope.user_read_currently_playing,
        Scope.playlist_read_collaborative,
        Scope.playlist_modify_public
    }
    """

    user_read_currently_playing = "user-read-currently-playing"
    playlist_read_collaborative = "playlist-read-collaborative"
    playlist_modify_private = "playlist-modify-private"
    user_read_playback_position = "user-read-playback-position"
    user_library_modify = "user-library-modify"
    user_top_read = "user-top-read"
    user_read_playback_state = "user-read-playback-state"
    user_read_email = "user-read-email"
    ugc_image_upload = "ugc-image-upload"
    user_read_private = "user-read-private"
    playlist_modify_public = "playlist-modify-public"
    user_library_read = "user-library-read"
    streaming = "streaming"
    user_read_recently_played = "user-read-recently-played"
    user_follow_read = "user-follow-read"
    user_follow_modify = "user-follow-modify"
    app_remote_control = "app-remote-control"
    playlist_read_private = "playlist-read-private"
    user_modify_playback_state = "user-modify-playback-state"

    @staticmethod
    def all() -> Set['Scope']:
        """Returns all of the authorization scopes"""

        return set(Scope)

    @staticmethod
    def make_string(scopes: Iterable['Scope']) -> str:
        """
        Converts an iterable of scopes to a space-separated string.

        * scopes: An iterable of scopes.

        returns: a space-separated string of scopes
        """
        return " ".join([scope.value for scope in scopes])

    @staticmethod
    def from_string(scope_string: str) -> Set['Scope']:
        """
        Converts a string of (usuallly space-separated) scopes into a
        set of scopes

        Any scope-strings that do not match any of the known scopes are
        ignored.

        * scope_string: a string of scopes

        returns: a set of scopes.
        """
        scope_string_list = re.split(pattern=r"[^\w-]+", string=scope_string)
        scopes = set()
        for scope_string in sorted(scope_string_list):
            try:
                scope = Scope(scope_string)
                scopes.add(scope)
            except ValueError:
                pass
        return scopes

from typing import Dict, Optional


class SpotifyException(Exception):

    def __init__(self, http_status: int, code: int, msg: str,
                 reason: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        self.http_status = http_status
        self.code = code
        self.msg = msg
        self.reason = reason
        # `headers` is used to support `Retry-After` in the event of a
        # 429 status code.
        if headers is None:
            headers = {}
        self.headers = headers

    def __str__(self):
        return 'http status: {0}, code:{1} - {2}, reason: {3}'.format(
            self.http_status, self.code, self.msg, self.reason)

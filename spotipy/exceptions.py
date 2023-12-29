class SpotifyException(Exception):

    def __init__(self, http_status, code, msg, reason=None, headers=None):
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
        return 'http status: {}, code:{} - {}, reason: {}'.format(
            self.http_status, self.code, self.msg, self.reason)

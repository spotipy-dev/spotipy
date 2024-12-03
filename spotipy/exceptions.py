class SpotifyBaseException(Exception):
    pass


class SpotifyException(SpotifyBaseException):

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


class SpotifyOauthError(SpotifyBaseException):
    """ Error during Auth Code or Implicit Grant flow """

    def __init__(self, message, error=None, error_description=None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super().__init__(message, *args, **kwargs)


class SpotifyStateError(SpotifyOauthError):
    """ The state sent and state received were different """

    def __init__(self, local_state=None, remote_state=None, message=None,
                 error=None, error_description=None, *args, **kwargs):
        if not message:
            message = ("Expected " + local_state + " but received "
                       + remote_state)
        super(SpotifyOauthError, self).__init__(message, error,
                                                error_description, *args,
                                                **kwargs)

class SpotifyBaseException(Exception):
    pass


class SpotifyException(SpotifyBaseException):
    """
    Exception raised for Spotify API errors.

    :param http_status: The HTTP status code returned by the API.
    :param code: The specific error code returned by the API.
    :param msg: The error message returned by the API.
    :param reason: (Optional) The reason for the error.
    :param headers: (Optional) The headers returned by the API.
    """

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
        return (f"http status: {self.http_status}, "
                f"code: {self.code} - {self.msg}, "
                f"reason: {self.reason}")


class SpotifyOauthError(SpotifyBaseException):
    """
    Exception raised for errors during Auth Code or Implicit Grant flow.

    :param message: The error message.
    :param error: (Optional) The specific error code.
    :param error_description: (Optional) A description of the error.
    """

    def __init__(self, message, error=None, error_description=None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super().__init__(message, *args, **kwargs)


class SpotifyStateError(SpotifyOauthError):
    """
    Exception raised when the state sent and state received are different.

    :param local_state: The state sent.
    :param remote_state: The state received.
    :param message: (Optional) The error message.
    :param error: (Optional) The specific error code.
    :param error_description: (Optional) A description of the error.
    """

    def __init__(self, local_state=None, remote_state=None, message=None,
                 error=None, error_description=None, *args, **kwargs):
        if not message:
            message = ("Expected " + local_state + " but received "
                       + remote_state)
        super(SpotifyOauthError, self).__init__(message, error,
                                                error_description, *args,
                                                **kwargs)

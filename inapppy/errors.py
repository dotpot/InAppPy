class InAppPyValidationError(BaseException):
    """ Base class for all validation errors """

    raw_response = None

    def __init__(self, message: str = None, raw_response: dict = None, *args, **kwargs):
        self.raw_response = raw_response
        super().__init__(message, raw_response, *args, **kwargs)


class GoogleError(InAppPyValidationError):
    def __init__(self, message, raw_response, *args, **kwargs):
        super().__init__(message, raw_response, *args, **kwargs)

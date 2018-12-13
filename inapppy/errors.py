class InAppPyValidationError(Exception):
    """ Base class for all validation errors """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GoogleError(InAppPyValidationError):
    raw_response = None

    def __init__(self, message, raw_response, *args, **kwargs):
        self.raw_response = raw_response
        super().__init__(message, raw_response, *args, **kwargs)

class InAppPyValidationError(Exception):
    """ Base class for all validation errors """

    raw_response = None
    message = None

    def __init__(self, message: str = None, raw_response: dict = None, *args, **kwargs):
        self.raw_response = raw_response
        self.message = message

        super().__init__(message, *args, **kwargs)

    def __str__(self):
        return f"InAppPyValidationError(message={self.message}, raw_response={self.raw_response})"


class GoogleError(InAppPyValidationError):
    def __init__(self, message: str = None, raw_response: dict = None, *args, **kwargs):
        super().__init__(message, raw_response, *args, **kwargs)

    def __str__(self):
        return f"GoogleError(message={self.message}, raw_response={self.raw_response})"

class InAppPyValidationError(Exception):
    """ Base class for all validation errors """
    raw_response = None

    def __init__(self, *args, **kwargs):
        self.raw_response = kwargs.pop('raw_response', None)
        super().__init__(*args, **kwargs)


class GoogleError(InAppPyValidationError):
    pass


class InAppPyValidationError(Exception):
    """ Base class for all validation errors """
    raw_response = None

    def __init__(self, raw_response=None):
        super(InAppPyValidationError, self).__init__()
        self.raw_response = raw_response

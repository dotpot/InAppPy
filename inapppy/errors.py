
class InAppPyValidationError(Exception):
    """ Base class for all validation errors """
    raw_response = None
    error_message = None

    def __init__(self, error_message=None):
        super(InAppPyValidationError, self).__init__()
        self.error_message = error_message

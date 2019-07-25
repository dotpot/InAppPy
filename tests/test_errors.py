from inapppy.errors import InAppPyValidationError, GoogleError


def test_base_error_plain_stringify():
    error = InAppPyValidationError()
    assert error
    assert str(error) == "InAppPyValidationError(message=None, raw_response=None)"


def test_base_error_message_stringify(generic_error_message):
    error = InAppPyValidationError(generic_error_message)
    assert str(error) == f"InAppPyValidationError(message={generic_error_message}, raw_response=None)"


def test_base_error_message_and_raw_response_stringify(generic_error_message, generic_raw_response):
    error = InAppPyValidationError(generic_error_message, generic_raw_response)
    assert str(error) == f"InAppPyValidationError(message={generic_error_message}, raw_response={generic_raw_response})"


def test_google_error_plain_stringify():
    error = GoogleError()
    assert error
    assert str(error) == "GoogleError(message=None, raw_response=None)"


def test_google_error_message_stringify(generic_error_message):
    error = GoogleError(generic_error_message)
    assert str(error) == f"GoogleError(message={generic_error_message}, raw_response=None)"


def test_google_error_message_and_raw_response_stringify(generic_error_message, generic_raw_response):
    error = GoogleError(generic_error_message, generic_raw_response)
    assert str(error) == f"GoogleError(message={generic_error_message}, raw_response={generic_raw_response})2"

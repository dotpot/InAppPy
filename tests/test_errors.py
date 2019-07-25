from inapppy.errors import InAppPyValidationError, GoogleError


def test_base_error_plain_stringify():
    error = InAppPyValidationError()
    assert error
    assert repr(error) == "InAppPyValidationError(message=None, raw_response=None)"
    assert str(error) == "InAppPyValidationError None None"


def test_base_error_message_stringify(generic_error_message):
    error = InAppPyValidationError(generic_error_message)
    assert repr(error) == f"InAppPyValidationError(message={generic_error_message!r}, raw_response=None)"
    assert str(error) == f"InAppPyValidationError {generic_error_message} None"


def test_base_error_message_and_raw_response_stringify(generic_error_message, generic_raw_response):
    error = InAppPyValidationError(generic_error_message, generic_raw_response)
    assert (
        repr(error) == f"InAppPyValidationError("
        f"message={generic_error_message!r}, raw_response={generic_raw_response!r})"
    )
    assert str(error) == "InAppPyValidationError error message {'foo': 'bar'}"


def test_google_error_plain_stringify():
    error = GoogleError()
    assert error
    assert repr(error) == "GoogleError(message=None, raw_response=None)"
    assert str(error) == "GoogleError None None"


def test_google_error_message_stringify(generic_error_message):
    error = GoogleError(generic_error_message)
    assert repr(error) == f"GoogleError(message={generic_error_message!r}, raw_response=None)"
    assert str(error) == f"GoogleError {generic_error_message} None"


def test_google_error_message_and_raw_response_stringify(generic_error_message, generic_raw_response):
    error = GoogleError(generic_error_message, generic_raw_response)
    assert repr(error) == f"GoogleError(message={generic_error_message!r}, raw_response={generic_raw_response!r})"
    assert str(error) == "GoogleError error message {'foo': 'bar'}"

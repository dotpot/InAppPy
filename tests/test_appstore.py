from unittest.mock import patch

import pytest

from inapppy import AppStoreValidator, InAppPyValidationError


def test_appstore_validator_initiation_simple(appstore_validator: AppStoreValidator):
    assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"


def test_appstore_validator_initiation_sandbox(appstore_validator_sandbox: AppStoreValidator):
    assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"


def test_appstore_validate_simple(appstore_validator: AppStoreValidator):
    with patch.object(AppStoreValidator, "post_json", return_value={"status": 0}) as mock_method:
        appstore_validator.validate(receipt="test-receipt", shared_secret="shared-secret")
        assert mock_method.call_count == 1
        assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"
        assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}

    with patch.object(AppStoreValidator, "post_json", return_value={"status": 0}) as mock_method:
        appstore_validator.validate(receipt="test-receipt")
        assert mock_method.call_count == 1
        assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"
        assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt"}


def test_appstore_validate_sandbox(appstore_validator_sandbox: AppStoreValidator):
    with patch.object(AppStoreValidator, "post_json", return_value={"status": 0}) as mock_method:
        appstore_validator_sandbox.validate(receipt="test-receipt", shared_secret="shared-secret")
        assert mock_method.call_count == 1
        assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"
        assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}

    with patch.object(AppStoreValidator, "post_json", return_value={"status": 0}) as mock_method:
        appstore_validator_sandbox.validate(receipt="test-receipt")
        assert mock_method.call_count == 1
        assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"
        assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt"}


def test_appstore_validate_attach_raw_response_to_the_exception(appstore_validator: AppStoreValidator):
    raw_response = {"status": 21000, "foo": "bar"}

    with pytest.raises(InAppPyValidationError) as ex:
        with patch.object(AppStoreValidator, "post_json", return_value=raw_response) as mock_method:
            appstore_validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert mock_method.call_count == 1
            assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}
            assert ex.raw_response is not None
            assert ex.raw_response == raw_response


def test_appstore_validate_attach_raw_response_to_the_exception_when_status_unkown(
    appstore_validator: AppStoreValidator,
):
    raw_response = {"status": "x", "foo": "bar"}

    with pytest.raises(InAppPyValidationError) as ex:
        with patch.object(AppStoreValidator, "post_json", return_value=raw_response) as mock_method:
            appstore_validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert mock_method.call_count == 1
            assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}
            assert ex.raw_response is not None
            assert ex.raw_response == raw_response


def test_appstore_auto_retry_wrong_env_request(appstore_validator_auto_retry_on_sandbox: AppStoreValidator):
    validator = appstore_validator_auto_retry_on_sandbox
    assert not validator.sandbox
    assert validator.auto_retry_wrong_env_request

    raw_response = {"status": 21007, "foo": "bar"}
    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", return_value=raw_response) as mock_method:
            validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert mock_method.call_count == 1
            assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}
            assert validator.sandbox is True

    raw_response = {"status": 21008, "foo": "bar"}
    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", return_value=raw_response) as mock_method:
            validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert validator.sandbox is False
            assert mock_method.call_count == 1
            assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert mock_method.call_args[0][0] == {"receipt-data": "test-receipt", "password": "shared-secret"}


def test_appstore_http_error_includes_raw_response(appstore_validator: AppStoreValidator):
    """Test that HTTP errors include raw_response with status code and content"""
    from unittest.mock import Mock

    # Mock a response that has status code but invalid JSON
    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.text = "Service Unavailable"
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")

    with pytest.raises(InAppPyValidationError) as exc_info:
        with patch("requests.post", return_value=mock_response):
            appstore_validator.post_json({"receipt-data": "test"})

    # Verify raw_response is not None and contains useful information
    assert exc_info.value.raw_response is not None
    assert "error" in exc_info.value.raw_response
    assert "status_code" in exc_info.value.raw_response
    assert exc_info.value.raw_response["status_code"] == 503
    assert "content" in exc_info.value.raw_response
    assert exc_info.value.raw_response["content"] == "Service Unavailable"


def test_appstore_network_error_includes_raw_response(appstore_validator: AppStoreValidator):
    """Test that network errors include raw_response with error details"""
    from requests.exceptions import RequestException

    with pytest.raises(InAppPyValidationError) as exc_info:
        with patch("requests.post", side_effect=RequestException("Connection timeout")):
            appstore_validator.post_json({"receipt-data": "test"})

    # Verify raw_response is not None and contains error information
    assert exc_info.value.raw_response is not None
    assert "error" in exc_info.value.raw_response
    assert "Connection timeout" in exc_info.value.raw_response["error"]

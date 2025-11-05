from unittest.mock import Mock, patch

import pytest

from inapppy import InAppPyValidationError
from inapppy.asyncio import AppStoreValidator


def test_appstore_validator_initiation_simple(appstore_validator: AppStoreValidator):
    assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"


def test_appstore_validator_initiation_sandbox(appstore_validator_sandbox):
    assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_validate_simple(appstore_validator: AppStoreValidator):
    async def post_json(self, request_json):
        assert request_json == {"receipt-data": "test-receipt", "password": "shared-secret"}
        return {"status": 0}

    async def post_json_no_secret(self, request_json):
        assert request_json == {"receipt-data": "test-receipt"}
        return {"status": 0}

    with patch.object(AppStoreValidator, "post_json", new=post_json):
        await appstore_validator.validate(receipt="test-receipt", shared_secret="shared-secret")
        assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"

    with patch.object(AppStoreValidator, "post_json", new=post_json_no_secret):
        await appstore_validator.validate(receipt="test-receipt")
        assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_validate_sandbox(appstore_validator_sandbox: AppStoreValidator):
    async def post_json(self, receipt):
        assert receipt == {"receipt-data": "test-receipt", "password": "shared-secret"}
        return {"status": 0}

    async def post_json_no_secret(self, receipt):
        assert receipt == {"receipt-data": "test-receipt"}
        assert receipt == {"receipt-data": "test-receipt"}
        return {"status": 0}

    with patch.object(AppStoreValidator, "post_json", new=post_json):
        await appstore_validator_sandbox.validate(receipt="test-receipt", shared_secret="shared-secret")
        assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"

    with patch.object(AppStoreValidator, "post_json", new=post_json_no_secret):
        await appstore_validator_sandbox.validate(receipt="test-receipt")
        assert appstore_validator_sandbox.url == "https://sandbox.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_validate_attach_raw_response_to_the_exception(appstore_validator: AppStoreValidator):
    raw_response = {"status": 21000, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {"receipt-data": "test-receipt", "password": "shared-secret"}
        return raw_response

    with pytest.raises(InAppPyValidationError) as ex:
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await appstore_validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert appstore_validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert ex.raw_response is not None
            assert ex.raw_response == raw_response


@pytest.mark.asyncio
async def test_appstore_auto_retry_wrong_env_request(appstore_validator_auto_retry_on_sandbox: AppStoreValidator):
    validator = appstore_validator_auto_retry_on_sandbox
    assert validator is not None
    assert not validator.sandbox
    assert validator.auto_retry_wrong_env_request

    raw_response = {"status": 21007, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {"receipt-data": "test-receipt", "password": "shared-secret"}
        return raw_response

    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            assert validator.sandbox is True

    raw_response = {"status": 21008, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {"receipt-data": "test-receipt", "password": "shared-secret"}
        return raw_response

    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await validator.validate(receipt="test-receipt", shared_secret="shared-secret")
            assert validator.sandbox is False
            assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_async_context_manager():
    """Test that async context manager properly initializes and returns self."""
    bundle_id = "com.test.app"
    validator = AppStoreValidator(bundle_id)

    # Verify session is None before entering context
    assert validator._session is None

    # Test async context manager
    async with validator as v:
        # Verify __aenter__ returns self
        assert v is validator
        # Verify session is initialized
        assert validator._session is not None

    # Verify session is closed after exiting context
    assert validator._session is None


@pytest.mark.asyncio
async def test_appstore_async_http_error_includes_raw_response(appstore_validator: AppStoreValidator):
    """Test that async HTTP errors include raw_response with status code and content"""
    from unittest.mock import AsyncMock, Mock

    # Create a mock response
    mock_resp = Mock()
    mock_resp.status = 503
    mock_resp.text = AsyncMock(return_value="Service Unavailable")

    # Create a mock session post that returns our mock response
    def mock_post(*args, **kwargs):
        class MockContext:
            async def __aenter__(self):
                return mock_resp

            async def __aexit__(self, *args):
                pass

        return MockContext()

    with pytest.raises(InAppPyValidationError) as exc_info:
        appstore_validator._session = Mock()
        appstore_validator._session.post = mock_post
        # Mock json.loads to raise ValueError (simulating invalid JSON)
        with patch("json.loads", side_effect=ValueError("Invalid JSON")):
            await appstore_validator.post_json({"receipt-data": "test"})

    # Verify raw_response is not None and contains useful information
    assert exc_info.value.raw_response is not None
    assert "error" in exc_info.value.raw_response
    assert "status_code" in exc_info.value.raw_response
    assert exc_info.value.raw_response["status_code"] == 503
    assert "content" in exc_info.value.raw_response
    assert exc_info.value.raw_response["content"] == "Service Unavailable"


@pytest.mark.asyncio
async def test_appstore_async_network_error_includes_raw_response(appstore_validator: AppStoreValidator):
    """Test that async network errors include raw_response with error details"""
    from aiohttp import ClientError

    # Create a mock session that raises ClientError
    def mock_post(*args, **kwargs):
        class MockContext:
            async def __aenter__(self):
                raise ClientError("Connection timeout")

            async def __aexit__(self, *args):
                pass

        return MockContext()

    with pytest.raises(InAppPyValidationError) as exc_info:
        appstore_validator._session = Mock()
        appstore_validator._session.post = mock_post
        await appstore_validator.post_json({"receipt-data": "test"})

    # Verify raw_response is not None and contains error information
    assert exc_info.value.raw_response is not None
    assert "error" in exc_info.value.raw_response
    assert "Connection timeout" in exc_info.value.raw_response["error"]

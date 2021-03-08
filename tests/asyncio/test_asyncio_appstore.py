from unittest.mock import patch

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

import pytest
from unittest.mock import patch

from inapppy import InAppPyValidationError
from inapppy.asyncio import AppStoreValidator


def test_appstore_validator_initiation_raises_if_no_bundle_id():
    with pytest.raises(InAppPyValidationError):
        AppStoreValidator(bundle_id="")


def test_appstore_validator_initiation_simple():
    validator = AppStoreValidator(bundle_id="test-bundle-id")
    assert validator is not None
    assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"


def test_appstore_validator_initiation_sandbox():
    validator = AppStoreValidator(bundle_id="test-bundle-id", sandbox=True)
    assert validator is not None
    assert validator.url == "https://sandbox.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_validate_simple():
    validator = AppStoreValidator(bundle_id="test-bundle-id")
    assert validator is not None

    async def post_json(self, request_json):
        assert request_json == {
            "receipt-data": "test-receipt",
            "password": "shared-secret",
        }
        return {"status": 0}

    async def post_json_no_secret(self, request_json):
        assert request_json == {"receipt-data": "test-receipt"}
        return {"status": 0}

    with patch.object(AppStoreValidator, "post_json", new=post_json):
        await validator.validate(
            receipt="test-receipt", shared_secret="shared-secret"
        )
        assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"

    with patch.object(AppStoreValidator, "post_json", new=post_json_no_secret):
        await validator.validate(receipt="test-receipt")
        assert validator.url == "https://buy.itunes.apple.com/verifyReceipt"


@pytest.mark.asyncio
async def test_appstore_validate_sandbox():
    validator = AppStoreValidator(bundle_id="test-bundle-id", sandbox=True)
    assert validator is not None

    async def post_json(self, receipt):
        assert receipt == {
            "receipt-data": "test-receipt",
            "password": "shared-secret",
        }
        return {"status": 0}

    async def post_json_no_secret(self, receipt):
        assert receipt == {"receipt-data": "test-receipt"}
        assert receipt == {"receipt-data": "test-receipt"}
        return {"status": 0}

    with patch.object(AppStoreValidator, "post_json", new=post_json):
        await validator.validate(
            receipt="test-receipt", shared_secret="shared-secret"
        )
        assert (
            validator.url == "https://sandbox.itunes.apple.com/verifyReceipt"
        )

    with patch.object(AppStoreValidator, "post_json", new=post_json_no_secret):
        await validator.validate(receipt="test-receipt")
        assert (
            validator.url == "https://sandbox.itunes.apple.com/verifyReceipt"
        )


@pytest.mark.asyncio
async def test_appstore_validate_attach_raw_response_to_the_exception():
    validator = AppStoreValidator(bundle_id="test-bundle-id")
    assert validator is not None

    raw_response = {"status": 21000, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {
            "receipt-data": "test-receipt",
            "password": "shared-secret",
        }
        return raw_response

    with pytest.raises(InAppPyValidationError) as ex:
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await validator.validate(
                receipt="test-receipt", shared_secret="shared-secret"
            )
            assert (
                validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            )
            assert ex.raw_response is not None
            assert ex.raw_response == raw_response


@pytest.mark.asyncio
async def test_appstore_auto_retry_wrong_env_request():
    validator = AppStoreValidator(
        bundle_id="test-bundle-id",
        sandbox=False,
        auto_retry_wrong_env_request=True,
    )
    assert validator is not None
    assert not validator.sandbox
    assert validator.auto_retry_wrong_env_request

    raw_response = {"status": 21007, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {
            "receipt-data": "test-receipt",
            "password": "shared-secret",
        }
        return raw_response

    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await validator.validate(
                receipt="test-receipt", shared_secret="shared-secret"
            )
            assert (
                validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            )
            assert validator.sandbox is True

    raw_response = {"status": 21008, "foo": "bar"}

    async def post_json(self, receipt):
        assert receipt == {
            "receipt-data": "test-receipt",
            "password": "shared-secret",
        }
        return raw_response

    with pytest.raises(InAppPyValidationError):
        with patch.object(AppStoreValidator, "post_json", new=post_json):
            await validator.validate(
                receipt="test-receipt", shared_secret="shared-secret"
            )
            assert validator.sandbox is False
            assert (
                validator.url == "https://buy.itunes.apple.com/verifyReceipt"
            )

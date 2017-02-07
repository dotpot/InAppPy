import pytest
from unittest.mock import patch

from inapppy.appstore import AppStoreValidator
from inapppy.errors import InAppPyValidationError


def test_appstore_validator_initiation_raises_if_no_bundle_id():
    with pytest.raises(InAppPyValidationError):
        AppStoreValidator(bundle_id='')


def test_appstore_validator_initiation_simple():
    validator = AppStoreValidator(bundle_id='test-bundle-id')
    assert validator is not None
    assert validator.url == 'https://buy.itunes.apple.com/verifyReceipt'


def test_appstore_validator_initiation_sandbox():
    validator = AppStoreValidator(bundle_id='test-bundle-id', sandbox=True)
    assert validator is not None
    assert validator.url == 'https://sandbox.itunes.apple.com/verifyReceipt'


def test_appstore_validate_simple():
    validator = AppStoreValidator(bundle_id='test-bundle-id')
    assert validator is not None

    with patch.object(AppStoreValidator, 'post_json', return_value={'status': 0}) as mock_method:
        validator.validate(receipt='test-receipt', shared_secret='shared-secret')
        assert mock_method.call_count == 1
        assert validator.url == 'https://buy.itunes.apple.com/verifyReceipt'
        assert mock_method.call_args[0][0] == {'receipt-data': 'test-receipt', 'password': 'shared-secret'}

    with patch.object(AppStoreValidator, 'post_json', return_value={'status': 0}) as mock_method:
        validator.validate(receipt='test-receipt')
        assert mock_method.call_count == 1
        assert validator.url == 'https://buy.itunes.apple.com/verifyReceipt'
        assert mock_method.call_args[0][0] == {'receipt-data': 'test-receipt'}


def test_appstore_validate_sandbox():
    validator = AppStoreValidator(bundle_id='test-bundle-id', sandbox=True)
    assert validator is not None

    with patch.object(AppStoreValidator, 'post_json', return_value={'status': 0}) as mock_method:
        validator.validate(receipt='test-receipt', shared_secret='shared-secret')
        assert mock_method.call_count == 1
        assert validator.url == 'https://sandbox.itunes.apple.com/verifyReceipt'
        assert mock_method.call_args[0][0] == {'receipt-data': 'test-receipt', 'password': 'shared-secret'}

    with patch.object(AppStoreValidator, 'post_json', return_value={'status': 0}) as mock_method:
        validator.validate(receipt='test-receipt')
        assert mock_method.call_count == 1
        assert validator.url == 'https://sandbox.itunes.apple.com/verifyReceipt'
        assert mock_method.call_args[0][0] == {'receipt-data': 'test-receipt'}


def test_appstore_validate_attach_raw_response_to_the_exception():
    validator = AppStoreValidator(bundle_id='test-bundle-id')
    assert validator is not None

    raw_response = {'status': 21000, 'foo': 'bar'}

    with pytest.raises(InAppPyValidationError) as ex:
        with patch.object(AppStoreValidator, 'post_json', return_value=raw_response) as mock_method:
            validator.validate(receipt='test-receipt', shared_secret='shared-secret')
            assert mock_method.call_count == 1
            assert validator.url == 'https://buy.itunes.apple.com/verifyReceipt'
            assert mock_method.call_args[0][0] == {'receipt-data': 'test-receipt', 'password': 'shared-secret'}
            assert ex.raw_response is not None
            assert ex.raw_response == raw_response

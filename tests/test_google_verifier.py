import datetime

import pytest
from unittest.mock import patch

from inapppy import googleplay, errors


def test_google_verify_non_subscription():
    with patch.object(googleplay, 'build', return_value=None):
        with patch.object(googleplay.GooglePlayVerifier, '_authorize', return_value=None):
            verifier = googleplay.GooglePlayVerifier('test-bundle-id', 'private_key_path', 30)
            with patch.object(verifier, 'get_subscriptions', return_value={}):
                with pytest.raises(NotImplementedError):
                    verifier.verify('test-token', 'test-product')


def test_google_verify_subscription():
    with patch.object(googleplay, 'build', return_value=None):
        with patch.object(googleplay.GooglePlayVerifier, '_authorize', return_value=None):
            verifier = googleplay.GooglePlayVerifier('test-bundle-id', 'private_key_path', 30)

            # expired
            with patch.object(verifier, 'get_subscriptions', return_value={'expiryTimeMillis': 666}):
                with pytest.raises(errors.GoogleError):
                    verifier.verify('test-token', 'test-product', is_subscription=True)

            # canceled
            with patch.object(verifier, 'get_subscriptions', return_value={'cancelReason': 666}):
                with pytest.raises(errors.GoogleError):
                    verifier.verify('test-token', 'test-product', is_subscription=True)

            # norm
            now = datetime.datetime.utcnow().timestamp()
            with patch.object(verifier, 'get_subscriptions', return_value={'expiryTimeMillis': now * 1000 + 10**10}):
                verifier.verify('test-token', 'test-product', is_subscription=True)

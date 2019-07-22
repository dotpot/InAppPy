import datetime

import pytest
from unittest.mock import patch

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import RequestMockBuilder, HttpMock

from inapppy import googleplay, errors, GooglePlayVerifier


def test_google_verify_subscription():
    with patch.object(googleplay, "build", return_value=None):
        with patch.object(
            googleplay.GooglePlayVerifier, "_authorize", return_value=None
        ):
            verifier = googleplay.GooglePlayVerifier(
                "test-bundle-id", "private_key_path", 30
            )

            # expired
            with patch.object(
                verifier,
                "check_purchase_subscription",
                return_value={"expiryTimeMillis": 666},
            ):
                with pytest.raises(errors.GoogleError):
                    verifier.verify("test-token", "test-product", is_subscription=True)

            # canceled
            with patch.object(
                verifier,
                "check_purchase_subscription",
                return_value={"cancelReason": 666},
            ):
                with pytest.raises(errors.GoogleError):
                    verifier.verify("test-token", "test-product", is_subscription=True)

            # norm
            now = datetime.datetime.utcnow().timestamp()
            with patch.object(
                verifier,
                "check_purchase_subscription",
                return_value={"expiryTimeMillis": now * 1000 + 10 ** 10},
            ):
                verifier.verify("test-token", "test-product", is_subscription=True)


def test_google_verify_product():
    with patch.object(googleplay, "build", return_value=None):
        with patch.object(
            googleplay.GooglePlayVerifier, "_authorize", return_value=None
        ):
            verifier = googleplay.GooglePlayVerifier(
                "test-bundle-id", "private_key_path", 30
            )

            # purchase
            with patch.object(
                verifier, "check_purchase_product", return_value={"purchaseState": 0}
            ):
                verifier.verify("test-token", "test-product")

            # cancelled
            with patch.object(
                verifier, "check_purchase_product", return_value={"purchaseState": 1}
            ):
                with pytest.raises(errors.GoogleError):
                    verifier.verify("test-token", "test-product")


def test_broken_receipt():
    mock = HttpMock(headers={'status': 400})
    mock.headers = {'status': 400}
    mock.data = b'{"reason": "Bad request"}'

    with patch.object(
        googleplay.GooglePlayVerifier, "_authorize", return_value=mock
    ):
        verifier = GooglePlayVerifier('bundle_id', 'private_key_path')

        with pytest.raises(HttpError):
            verifier.verify('broken_purchase_token', 'product_scu')

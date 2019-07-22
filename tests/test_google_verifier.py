import datetime
import os
from unittest.mock import patch

import httplib2
import pytest
from googleapiclient.http import HttpMock, RequestMockBuilder

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


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def datafile(filename):
    return os.path.join(DATA_DIR, filename)


def test_broken_receipt():
    with patch.object(
        googleplay.GooglePlayVerifier, "_authorize", return_value=None
    ):
        verifier = GooglePlayVerifier('bundle_id', 'private_key_path')

        auth = HttpMock(datafile("androidpublisher.json"), headers={'status': 200})

        request_mock_builder = RequestMockBuilder(
            {
                'androidpublisher.purchases.products.get': (
                    httplib2.Response({'status': 400, "reason": b"Bad request"}),
                    b'{"reason": "Bad request"}',
                )
            }
        )
        build_mock_result = googleplay.build("androidpublisher", "v3", http=auth, requestBuilder=request_mock_builder)

        with patch.object(googleplay, "build", return_value=build_mock_result):
            with pytest.raises(errors.GoogleError, match="Bad request"):
                verifier.verify('broken_purchase_token', 'product_scu')

        request_mock_builder = RequestMockBuilder(
            {
                'androidpublisher.purchases.subscriptions.get': (
                    httplib2.Response({'status': 400, "reason": b"Bad request"}),
                    b'{"reason": "Bad request"}',
                )
            }
        )
        build_mock_result = googleplay.build("androidpublisher", "v3", http=auth, requestBuilder=request_mock_builder)

        with patch.object(googleplay, "build", return_value=build_mock_result):
            with pytest.raises(errors.GoogleError, match="Bad request"):
                verifier.verify('broken_purchase_token', 'product_scu', is_subscription=True)

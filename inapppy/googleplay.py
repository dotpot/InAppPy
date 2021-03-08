import base64
import datetime
import json
import os
from typing import Union

import httplib2
import rsa
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from inapppy.errors import GoogleError, InAppPyError, InAppPyValidationError


def make_pem(public_key: str) -> str:
    value = (public_key[i : i + 64] for i in range(0, len(public_key), 64))  # noqa: E203
    return "\n".join(("-----BEGIN PUBLIC KEY-----", "\n".join(value), "-----END PUBLIC KEY-----"))


class GooglePlayValidator:
    purchase_state_ok = 0

    def __init__(self, bundle_id: str, api_key: str, default_valid_purchase_state: int = 0) -> None:
        """
        Arguments:
            bundle_id: str - Also known as Android app's package name. E.g.:
                "com.example.calendar".

            api_key: str - Application's Base64-encoded RSA public key.
                As of 03.19 this can be found in Google Play Console under
                Services & APIs.

            default_valid_purchase_state: int - Accepted purchase state.
        """
        if not bundle_id:
            raise InAppPyValidationError("bundle_id cannot be empty.")

        elif not api_key:
            raise InAppPyValidationError("api_key cannot be empty.")

        self.bundle_id = bundle_id
        self.purchase_state_ok = default_valid_purchase_state

        pem = make_pem(api_key)

        try:
            self.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(pem)
        except TypeError:
            raise InAppPyValidationError("Bad API key")

    def validate(self, receipt: str, signature: str) -> dict:
        if not self._validate_signature(receipt, signature):
            raise InAppPyValidationError("Bad signature")

        try:
            receipt_json = json.loads(receipt)

            if receipt_json["packageName"] != self.bundle_id:
                raise InAppPyValidationError("Bundle ID  mismatch")

            elif receipt_json["purchaseState"] != self.purchase_state_ok:
                raise InAppPyValidationError("Item is not purchased")

            return receipt_json
        except (KeyError, ValueError):
            raise InAppPyValidationError("Bad receipt")

    def _validate_signature(self, receipt: str, signature: str) -> bool:
        try:
            sig = base64.standard_b64decode(signature)
            return rsa.verify(receipt.encode(), sig, self.public_key)
        except BaseException:
            return False


class GoogleVerificationResult:
    """Google verification result class."""

    raw_response: dict = {}
    is_expired: bool = False
    is_canceled: bool = False

    def __init__(self, raw_response: dict, is_expired: bool, is_canceled: bool):
        self.raw_response = raw_response
        self.is_expired = is_expired
        self.is_canceled = is_canceled

    def __repr__(self):
        return (
            f"GoogleVerificationResult("
            f"raw_response={self.raw_response}, "
            f"is_expired={self.is_expired}, "
            f"is_canceled={self.is_canceled})"
        )


class GooglePlayVerifier:
    DEFAULT_AUTH_SCOPE = "https://www.googleapis.com/auth/androidpublisher"

    def __init__(self, bundle_id: str, play_console_credentials: Union[str, dict], http_timeout: int = 15) -> None:
        """
        Arguments:
            bundle_id: str - Also known as Android app's package name.
            play_console_credentials - Path or dict contents of Google's Service Credentials
            http_timeout: int - HTTP connection timeout.
        """
        self.bundle_id = bundle_id
        self.play_console_credentials = play_console_credentials
        self.http_timeout = http_timeout
        self.http = self._authorize()

    @staticmethod
    def _ms_timestamp_expired(ms_timestamp: str) -> bool:
        now = datetime.datetime.utcnow()

        # Return if it's 0/None, expired.
        if not ms_timestamp:
            return True

        ms_timestamp_value = int(ms_timestamp) / 1000

        # Return if it's 0, expired.
        if not ms_timestamp_value:
            return True

        return datetime.datetime.utcfromtimestamp(ms_timestamp_value) < now

    @staticmethod
    def _create_credentials(play_console_credentials: Union[str, dict], scope_str: str):
        # If str, assume it's a filepath
        if isinstance(play_console_credentials, str):
            if not os.path.exists(play_console_credentials):
                raise InAppPyError(f"Google play console credentials file does not exist: {play_console_credentials}")
            return ServiceAccountCredentials.from_json_keyfile_name(play_console_credentials, scope_str)
        # If dict, assume parsed json
        if isinstance(play_console_credentials, dict):
            return ServiceAccountCredentials.from_json_keyfile_dict(play_console_credentials, scope_str)
        raise InAppPyError(
            f"Unknown play console credentials format: {repr(play_console_credentials)}, "
            "expected 'dict' or 'str' types"
        )

    def _authorize(self):
        http = httplib2.Http(timeout=self.http_timeout)
        credentials = self._create_credentials(self.play_console_credentials, self.DEFAULT_AUTH_SCOPE)
        http = credentials.authorize(http)
        return http

    def check_purchase_subscription(self, purchase_token: str, product_sku: str, service) -> dict:
        try:
            purchases = service.purchases()
            subscriptions = purchases.subscriptions()
            subscriptions_get = subscriptions.get(
                packageName=self.bundle_id, subscriptionId=product_sku, token=purchase_token
            )
            result = subscriptions_get.execute(http=self.http)
            return result
        except HttpError as e:
            if e.resp.status == 400:
                raise GoogleError(e.resp.reason, repr(e))
            else:
                raise e

    def check_purchase_product(self, purchase_token: str, product_sku: str, service) -> dict:
        try:
            purchases = service.purchases()
            products = purchases.products()
            products_get = products.get(packageName=self.bundle_id, productId=product_sku, token=purchase_token)
            result = products_get.execute(http=self.http)
            return result
        except HttpError as e:
            if e.resp.status == 400:
                raise GoogleError(e.resp.reason, repr(e))
            else:
                raise e

    def verify(self, purchase_token: str, product_sku: str, is_subscription: bool = False) -> dict:
        service = build("androidpublisher", "v3", http=self.http)

        if is_subscription:
            result = self.check_purchase_subscription(purchase_token, product_sku, service)
            cancel_reason = int(result.get("cancelReason", 0))

            if cancel_reason != 0:
                raise GoogleError("Subscription is canceled", result)

            ms_timestamp = result.get("expiryTimeMillis", 0)

            if self._ms_timestamp_expired(ms_timestamp):
                raise GoogleError("Subscription expired", result)
        else:
            result = self.check_purchase_product(purchase_token, product_sku, service)
            purchase_state = int(result.get("purchaseState", 1))

            if purchase_state != 0:
                raise GoogleError("Purchase cancelled", result)

        return result

    def verify_with_result(
        self, purchase_token: str, product_sku: str, is_subscription: bool = False
    ) -> GoogleVerificationResult:
        """Verifies by returning verification result instead of raising an error,
        basically it's and better alternative to verify method."""
        service = build("androidpublisher", "v3", http=self.http)
        verification_result = GoogleVerificationResult({}, False, False)

        if is_subscription:
            result = self.check_purchase_subscription(purchase_token, product_sku, service)
            verification_result.raw_response = result

            cancel_reason = int(result.get("cancelReason", 0))
            if cancel_reason != 0:
                verification_result.is_canceled = True

            ms_timestamp = result.get("expiryTimeMillis", 0)
            if self._ms_timestamp_expired(ms_timestamp):
                verification_result.is_expired = True
        else:
            result = self.check_purchase_product(purchase_token, product_sku, service)
            verification_result.raw_response = result

            purchase_state = int(result.get("purchaseState", 1))
            if purchase_state != 0:
                verification_result.is_canceled = True

        return verification_result

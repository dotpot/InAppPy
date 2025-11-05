import datetime
import warnings

import requests
from requests.exceptions import RequestException

from inapppy.errors import InAppPyValidationError

# https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html
# `Table 2-1  Status codes`
api_result_ok = 0
api_result_errors = {
    21000: InAppPyValidationError("Bad json"),
    21002: InAppPyValidationError("Bad data"),
    21003: InAppPyValidationError("Receipt authentication"),
    21004: InAppPyValidationError("Shared secret mismatch"),
    21005: InAppPyValidationError("Server is unavailable"),
    21006: InAppPyValidationError("Subscription has expired"),
    # two following errors can use auto_retry_wrong_env_request.
    21007: InAppPyValidationError("Sandbox receipt was sent to the production env"),
    21008: InAppPyValidationError("Production receipt was sent to the sandbox env"),
    21009: InAppPyValidationError("Internal data access error"),
    21010: InAppPyValidationError("The user account cannot be found or has been deleted"),
}


class AppStoreVerificationResult:
    """App Store verification result class."""

    raw_response: dict = {}
    is_expired: bool = False
    is_cancelled: bool = False

    def __init__(self, raw_response: dict, is_expired: bool, is_cancelled: bool):
        self.raw_response = raw_response
        self.is_expired = is_expired
        self.is_cancelled = is_cancelled

    def __repr__(self):
        return (
            f"AppStoreVerificationResult("
            f"raw_response={self.raw_response}, "
            f"is_expired={self.is_expired}, "
            f"is_cancelled={self.is_cancelled})"
        )


class AppStoreValidator:
    def __init__(
        self,
        bundle_id: str = "",
        sandbox: bool = False,
        auto_retry_wrong_env_request: bool = False,
        http_timeout: int = None,
    ):
        """Constructor for AppStoreValidator

        :param bundle_id: apple bundle id (no longer required).
        :param sandbox: sandbox mode ?
        :param auto_retry_wrong_env_request: auto retry on wrong env ?
        """
        if bundle_id:
            warnings.warn(
                "bundle_id will be removed in version 3, since it's not used here.",
                PendingDeprecationWarning,
            )

        self.bundle_id = bundle_id
        self.sandbox = sandbox
        self.http_timeout = http_timeout
        self.auto_retry_wrong_env_request = auto_retry_wrong_env_request

        self._change_url_by_sandbox()

    def _change_url_by_sandbox(self):
        self.url = (
            "https://sandbox.itunes.apple.com/verifyReceipt"
            if self.sandbox
            else "https://buy.itunes.apple.com/verifyReceipt"
        )

    def _prepare_receipt(self, receipt: str, shared_secret: str, exclude_old_transactions: bool) -> dict:
        receipt_json = {"receipt-data": receipt}

        if shared_secret:
            receipt_json["password"] = shared_secret

        if exclude_old_transactions:
            receipt_json["exclude-old-transactions"] = True

        return receipt_json

    def post_json(self, request_json: dict) -> dict:
        self._change_url_by_sandbox()

        response = None
        try:
            response = requests.post(self.url, json=request_json, timeout=self.http_timeout)
            return response.json()
        except (ValueError, RequestException) as e:
            # Build raw_response with available information
            raw_response = {"error": str(e)}

            # Try to include response details if available
            if response is not None:
                raw_response["status_code"] = response.status_code
                try:
                    raw_response["content"] = response.text
                except Exception:
                    pass

            raise InAppPyValidationError("HTTP error", raw_response=raw_response)

    @staticmethod
    def _ms_timestamp_expired(ms_timestamp: str) -> bool:
        """Check if a millisecond timestamp has expired.

        :param ms_timestamp: timestamp in milliseconds as string
        :return: True if expired, False otherwise
        """
        now = datetime.datetime.utcnow()

        # Return if it's 0/None, expired.
        if not ms_timestamp:
            return True

        try:
            ms_timestamp_value = int(ms_timestamp) / 1000
        except (ValueError, TypeError):
            return True

        # Return if it's 0, expired.
        if not ms_timestamp_value:
            return True

        return datetime.datetime.utcfromtimestamp(ms_timestamp_value) < now

    @staticmethod
    def _check_subscription_expired(receipt_info: dict) -> bool:
        """Check if subscription is expired based on latest_receipt_info.

        :param receipt_info: latest receipt info from Apple's response
        :return: True if expired, False otherwise
        """
        if not receipt_info:
            return True

        # Get the expires_date_ms from the latest receipt
        expires_date_ms = receipt_info.get("expires_date_ms", "0")
        return AppStoreValidator._ms_timestamp_expired(expires_date_ms)

    @staticmethod
    def _check_subscription_cancelled(receipt_info: dict) -> bool:
        """Check if subscription is cancelled based on cancellation_date.

        :param receipt_info: latest receipt info from Apple's response
        :return: True if cancelled, False otherwise
        """
        if not receipt_info:
            return False

        # If cancellation_date or cancellation_date_ms exists, subscription was cancelled/refunded
        return "cancellation_date" in receipt_info or "cancellation_date_ms" in receipt_info

    def validate(
        self,
        receipt: str,
        shared_secret: str = None,
        exclude_old_transactions: bool = False,
    ) -> dict:
        """Validates receipt against apple services.

        :param receipt: receipt
        :param shared_secret: optional shared secret.
        :param exclude_old_transactions: optional to include only the latest renewal transaction
        :return: validation result or exception.
        """
        receipt_json = self._prepare_receipt(receipt, shared_secret, exclude_old_transactions)

        api_response = self.post_json(receipt_json)
        status = api_response.get("status", "unknown")

        # Check retry case.
        if self.auto_retry_wrong_env_request and status in [21007, 21008]:
            # switch environment
            self.sandbox = not self.sandbox

            api_response = self.post_json(receipt_json)
            status = api_response["status"]

        if status != api_result_ok:
            error = api_result_errors.get(status, InAppPyValidationError("Unknown API status"))
            error.raw_response = api_response

            raise error

        return api_response

    def verify_with_result(
        self,
        receipt: str,
        shared_secret: str = None,
        exclude_old_transactions: bool = False,
    ) -> AppStoreVerificationResult:
        """Validates receipt and returns verification result instead of raising an error.

        This is an alternative to validate() method that returns a result object
        with is_expired and is_cancelled properties instead of raising exceptions.

        :param receipt: receipt
        :param shared_secret: optional shared secret.
        :param exclude_old_transactions: optional to include only the latest renewal transaction
        :return: AppStoreVerificationResult with validation details
        """
        try:
            api_response = self.validate(receipt, shared_secret, exclude_old_transactions)
        except InAppPyValidationError as e:
            # If validation fails, return result with raw_response from exception
            api_response = getattr(e, "raw_response", {})

        # Get latest receipt info (last element in array as it's the most recent)
        latest_receipt_info_list = api_response.get("latest_receipt_info", [])
        latest_receipt_info = latest_receipt_info_list[-1] if latest_receipt_info_list else {}

        # Check if subscription is expired or cancelled
        is_expired = self._check_subscription_expired(latest_receipt_info)
        is_cancelled = self._check_subscription_cancelled(latest_receipt_info)

        return AppStoreVerificationResult(raw_response=api_response, is_expired=is_expired, is_cancelled=is_cancelled)

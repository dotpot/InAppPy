from aiohttp import ClientError, ClientSession, ClientTimeout

from ..appstore import AppStoreValidator, api_result_errors, api_result_ok
from ..errors import InAppPyValidationError


class AppStoreValidator(AppStoreValidator):
    """The asyncio version of the app store validator."""

    def __init__(
        self,
        bundle_id: str = "",
        sandbox: bool = False,
        auto_retry_wrong_env_request: bool = False,
        http_timeout: int = None,
    ):
        super().__init__(bundle_id, sandbox, auto_retry_wrong_env_request, http_timeout)
        self._session = None

    async def __aenter__(self):
        self._session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()
        self._session = None

    async def post_json(self, request_json: dict) -> dict:
        self._change_url_by_sandbox()
        response_text = None
        status_code = None
        try:
            async with self._session.post(
                self.url, json=request_json, timeout=ClientTimeout(total=self.http_timeout)
            ) as resp:
                status_code = resp.status
                response_text = await resp.text()
                # Try to parse as JSON
                import json

                return json.loads(response_text)
        except (ValueError, ClientError) as e:
            # Build raw_response with available information
            raw_response = {"error": str(e)}

            # Try to include response details if available
            if status_code is not None:
                raw_response["status_code"] = status_code
            if response_text is not None:
                raw_response["content"] = response_text

            raise InAppPyValidationError("HTTP error", raw_response=raw_response)

    async def validate(self, receipt: str, shared_secret: str = None, exclude_old_transactions: bool = False) -> dict:
        """Validates receipt against apple services.

        :param receipt: receipt
        :param shared_secret: optional shared secret.
        :param exclude_old_transactions: optional to include only the latest renewal transaction
        :return: validation result or exception.
        """
        receipt_json = self._prepare_receipt(receipt, shared_secret, exclude_old_transactions)

        api_response = await self.post_json(receipt_json)
        status = api_response["status"]

        # Check retry case.
        if self.auto_retry_wrong_env_request and status in [21007, 21008]:
            # switch environment
            self.sandbox = not self.sandbox

            api_response = await self.post_json(receipt_json)
            status = api_response["status"]

        if status != api_result_ok:
            error = api_result_errors.get(status, InAppPyValidationError("Unknown API status"))
            error.raw_response = api_response

            raise error

        return api_response

from inapppy.errors import InAppPyValidationError

from requests.exceptions import RequestException
import requests

# https://developer.apple.com/library/content/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html
# `Table 2-1  Status codes`
api_result_ok = 0
api_result_errors = {
    21000: InAppPyValidationError('Bad json'),
    21002: InAppPyValidationError('Bad data'),
    21003: InAppPyValidationError('Receipt authentication'),
    21004: InAppPyValidationError('Shared secret mismatch'),
    21005: InAppPyValidationError('Server is unavailable'),
    21006: InAppPyValidationError('Subscription has expired'),

    # two following errors can use auto_retry_wrong_env_request.
    21007: InAppPyValidationError('Sandbox receipt was sent to the production env'),
    21008: InAppPyValidationError('Production receipt was sent to the sandbox env'),
}


class AppStoreValidator(object):
    bundle_id = None
    sandbox = None
    url = None
    auto_retry_wrong_env_request = False

    def __init__(self, bundle_id, sandbox=False, auto_retry_wrong_env_request=False, http_timeout=None):
        """ Constructor for AppStoreValidator

        :param bundle_id: apple bundle id
        :param sandbox: sandbox mode ?
        :param auto_retry_wrong_env_request: auto retry on wrong env ?
        """
        self.bundle_id = bundle_id
        self.sandbox = sandbox
        self.http_timeout = http_timeout

        if not self.bundle_id:
            raise InAppPyValidationError('`bundle_id` cannot be empty')

        self.auto_retry_wrong_env_request = auto_retry_wrong_env_request

        self._change_url_by_sandbox()

    def _change_url_by_sandbox(self):
        self.url = ('https://sandbox.itunes.apple.com/verifyReceipt' if self.sandbox else
                    'https://buy.itunes.apple.com/verifyReceipt')

    def post_json(self, request_json):
        self._change_url_by_sandbox()

        try:
            return requests.post(self.url, json=request_json, timeout=self.http_timeout).json()
        except (ValueError, RequestException):
            raise InAppPyValidationError('HTTP error')

    def validate(self, receipt, shared_secret=None, exclude_old_transactions=False):
        """ Validates receipt against apple services.

        :param receipt: receipt
        :param shared_secret: optional shared secret.
        :param exclude_old_transactions: optional to include only the latest renewal transaction
        :return: validation result or exception.
        """
        receipt_json = {'receipt-data': receipt}

        if shared_secret:
            receipt_json['password'] = shared_secret

        if exclude_old_transactions:
            receipt_json['exclude-old-transcations'] = True

        # Do a request.
        api_response = self.post_json(receipt_json)
        status = api_response['status']

        # Check retry case.
        if self.auto_retry_wrong_env_request and status in [21007, 21008]:
            # switch environment
            self.sandbox = not self.sandbox

            api_response = self.post_json(receipt_json)
            status = api_response['status']

        if status != api_result_ok:
            error = api_result_errors.get(status, InAppPyValidationError('Unknown API status'))
            error.raw_response = api_response

            raise error

        return api_response

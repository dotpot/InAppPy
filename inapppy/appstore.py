from inapppy.errors import InAppPyValidationError

from requests.exceptions import RequestException
import requests


api_result_ok = 0
api_result_errors = {
    21000: InAppPyValidationError('Bad json'),
    21002: InAppPyValidationError('Bad data'),
    21003: InAppPyValidationError('Receipt authentication'),
    21004: InAppPyValidationError('Shared secret mismatch'),
    21005: InAppPyValidationError('Server is unavailable'),
    21006: InAppPyValidationError('Subscription has expired'),
    21007: InAppPyValidationError('Sandbox receipt was sent to the production env'),
    21008: InAppPyValidationError('Production receipt was sent to the sandbox env'),
}


class AppStoreValidator(object):
    bundle_id = None
    sandbox = None
    url = None

    def __init__(self, bundle_id, sandbox=False):
        self.bundle_id = bundle_id
        self.sandbox = sandbox

        if not self.bundle_id:
            raise InAppPyValidationError('`bundle_id` cannot be empty')

        self._change_url_by_sandbox()

    def _change_url_by_sandbox(self):
        self.url = ('https://sandbox.itunes.apple.com/verifyReceipt' if self.sandbox else
                    'https://buy.itunes.apple.com/verifyReceipt')

    def post_json(self, request_json):
        self._change_url_by_sandbox()

        return requests.post(self.url, json=request_json).json()

    def validate(self, receipt, shared_secret=None):
        receipt_json = {'receipt-data': receipt}

        # if shared secret is provided, attach it as `password`.
        if shared_secret:
            receipt_json['password'] = shared_secret

        try:
            api_response = self.post_json(receipt_json)
        except (ValueError, RequestException):
            raise InAppPyValidationError('HTTP error')

        status = api_response['status']
        if status != api_result_ok:
            error = api_result_errors.get(status, InAppPyValidationError('Unknown API status'))
            error.raw_response = api_response

            raise error

        return api_response

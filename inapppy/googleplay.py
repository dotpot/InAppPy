import datetime
import json
import base64

import rsa
import httplib2

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from inapppy.errors import InAppPyValidationError, GoogleError

purchase_state_ok = 0


def make_pem(public_key):
    return '\n'.join((
        '-----BEGIN PUBLIC KEY-----',
        '\n'.join(public_key[i:i+64] for i in range(0, len(public_key), 64)),
        '-----END PUBLIC KEY-----'
    ))


class GooglePlayValidator(object):

    def __init__(self, bundle_id, api_key):
        self.bundle_id = bundle_id
        if not self.bundle_id:
            raise InAppPyValidationError('`bundle_id` cannot be empty.')

        pem = make_pem(api_key)
        try:
            self.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(pem)
        except TypeError:
            raise InAppPyValidationError('Bad api key')

    def validate(self, receipt, signature):
        ok = self._validate_signature(receipt, signature)

        if not ok:
            raise InAppPyValidationError('Bad signature')

        try:
            receipt_json = json.loads(receipt)

            if receipt_json['packageName'] != self.bundle_id:
                raise InAppPyValidationError('Bundle id mismatch')

            if receipt_json['purchaseState'] != purchase_state_ok:
                raise InAppPyValidationError('Item is not purchased')

            return receipt_json
        except (KeyError, ValueError):
            raise InAppPyValidationError('Bad receipt')

    def _validate_signature(self, receipt, signature):
        try:
            sig = base64.standard_b64decode(signature)
            return rsa.verify(receipt.encode(), sig, self.public_key)
        except (rsa.VerificationError, TypeError, ValueError, BaseException):
            return False


def _ms_timestamp_expired(ms_timestamp):
    now = datetime.datetime.utcnow()
    dt = datetime.datetime.fromtimestamp(int(ms_timestamp) / 1000)
    return dt < now


class GooglePlayVerifier:
    def __init__(self, bundle_id, private_key_path, http_timeout):
        self.bundle_id = bundle_id
        self.private_key_path = private_key_path
        self.http_timeout = http_timeout
        self.http = self._authorize()


    def _authorize(self):
        http = httplib2.Http(timeout=self.http_timeout)
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.private_key_path,
            'https://www.googleapis.com/auth/androidpublisher'
        )
        http = credentials.authorize(http)
        return http


    def get_subscriptions(self, purchase_token, product_sku, service):
        return service.purchases().subscriptions().get(
            packageName=self.bundle_id,
            subscriptionId=product_sku,
            token=purchase_token
        ).execute(http=self.http)


    def verify(self, purchase_token, product_sku, is_subscription=False):
        service = build("androidpublisher", "v3", http=self.http)
        if is_subscription:
            subscriptions = self.get_subscriptions(purchase_token, product_sku, service)
            cancel_reason = int(subscriptions.get('cancelReason', 0))
            if cancel_reason != 0:
                raise GoogleError('Subscription is canceled', subscriptions)
            ms_timestamp = subscriptions.get('expiryTimeMillis', 0)
            if _ms_timestamp_expired(ms_timestamp):
                raise GoogleError('Subscription expired', subscriptions)
        else:
            raise NotImplementedError()
        return subscriptions

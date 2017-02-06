import json
import base64

import rsa

from inapppy.errors import InAppPyValidationError


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

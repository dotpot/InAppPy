InAppPy
=======
|travis| |pypi| |downloads|

.. |travis| image:: https://travis-ci.org/dotpot/InAppPy.svg?branch=master
    :target: https://travis-ci.org/dotpot/InAppPy
.. |pypi| image:: https://badge.fury.io/py/inapppy.svg
    :target: https://badge.fury.io/py/inapppy
.. |downloads| image:: https://img.shields.io/pypi/dm/inapppy.svg
    :target: https://pypi.python.org/pypi/inapppy


Table of contents
=================

1. Introduction
2. Installation
3. Google Play (`receipt` + `signature`)
4. Google Play (verification)
5. Google Play (verification with result)
6. App Store (`receipt` + using optional `shared-secret`)
7. App Store Response (`validation_result` / `raw_response`) example
8. App Store, **asyncio** version (available in the inapppy.asyncio package)
9. Development


1. Introduction
===============

In-app purchase validation library for `Apple AppStore` and `GooglePlay` (`App Store` validator have **async** support!).

2. Installation
===============
::

    pip install inapppy


3. Google Play (validates `receipt` against provided `signature` using RSA)
===========================================================================
.. code:: python

    from inapppy import GooglePlayValidator, InAppPyValidationError


    bundle_id = 'com.yourcompany.yourapp'
    api_key = 'API key from the developer console'
    validator = GooglePlayValidator(bundle_id, api_key)

    try:
        # receipt means `androidData` in result of purchase
        # signature means `signatureAndroid` in result of purchase
        validation_result = validator.validate('receipt', 'signature')
    except InAppPyValidationError:
        # handle validation error
        pass


4. Google Play verification
===========================
.. code:: python

    from inapppy import GooglePlayVerifier, errors


    def google_validator(receipt):
        """
        Accepts receipt, validates in Google.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            GOOGLE_SERVICE_ACCOUNT_KEY_FILE,
        )
        response = {'valid': False, 'transactions': []}
        try:
            result = verifier.verify(
                purchase_token,
                product_sku,
				is_subscription=True
            )
            response['valid'] = True
            response['transactions'].append(
                (result['orderId'], product_sku)
            )
        except errors.GoogleError as exc:
            logging.error('Purchase validation failed {}'.format(exc))
        return response


5. Google Play verification (with result)
=========================================
Alternative to `.verify` method, instead of raising an error result class will be returned.

.. code:: python

    from inapppy import GooglePlayVerifier, errors


    def google_validator(receipt):
        """
        Accepts receipt, validates in Google.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            GOOGLE_SERVICE_ACCOUNT_KEY_FILE,
        )
        response = {'valid': False, 'transactions': []}

        result = verifier.verify_with_result(
            purchase_token,
            product_sku,
            is_subscription=True
        )

        # result contains data
        raw_response = result.raw_response
        is_canceled = result.is_canceled
        is_expired = result.is_expired

        return result


6. App Store (validates `receipt` using optional `shared-secret` against iTunes service)
========================================================================================
.. code:: python

    from inapppy import AppStoreValidator, InAppPyValidationError


    bundle_id = 'com.yourcompany.yourapp'
    auto_retry_wrong_env_request=False # if True, automatically query sandbox endpoint if
                                       # validation fails on production endpoint
    validator = AppStoreValidator(bundle_id, auto_retry_wrong_env_request=auto_retry_wrong_env_request)

    try:
        exclude_old_transactions=False # if True, include only the latest renewal transaction
        validation_result = validator.validate('receipt', 'optional-shared-secret', exclude_old_transactions=exclude_old_transactions)
    except InAppPyValidationError as ex:
        # handle validation error
        response_from_apple = ex.raw_response  # contains actual response from AppStore service.
        pass



7. App Store Response (`validation_result` / `raw_response`) example
====================================================================
.. code:: json

    {
        "latest_receipt": "MIIbngYJKoZIhvcNAQcCoIIbj...",
        "status": 0,
        "receipt": {
            "download_id": 0,
            "receipt_creation_date_ms": "1486371475000",
            "application_version": "2",
            "app_item_id": 0,
            "receipt_creation_date": "2017-02-06 08:57:55 Etc/GMT",
            "original_purchase_date": "2013-08-01 07:00:00 Etc/GMT",
            "request_date_pst": "2017-02-06 04:41:09 America/Los_Angeles",
            "original_application_version": "1.0",
            "original_purchase_date_pst": "2013-08-01 00:00:00 America/Los_Angeles",
            "request_date_ms": "1486384869996",
            "bundle_id": "com.yourcompany.yourapp",
            "request_date": "2017-02-06 12:41:09 Etc/GMT",
            "original_purchase_date_ms": "1375340400000",
            "in_app": [{
                "purchase_date_ms": "1486371474000",
                "web_order_line_item_id": "1000000034281189",
                "original_purchase_date_ms": "1486371475000",
                "original_purchase_date": "2017-02-06 08:57:55 Etc/GMT",
                "expires_date_pst": "2017-02-06 01:00:54 America/Los_Angeles",
                "original_purchase_date_pst": "2017-02-06 00:57:55 America/Los_Angeles",
                "purchase_date_pst": "2017-02-06 00:57:54 America/Los_Angeles",
                "expires_date_ms": "1486371654000",
                "expires_date": "2017-02-06 09:00:54 Etc/GMT",
                "original_transaction_id": "1000000271014363",
                "purchase_date": "2017-02-06 08:57:54 Etc/GMT",
                "quantity": "1",
                "is_trial_period": "false",
                "product_id": "com.yourcompany.yourapp",
                "transaction_id": "1000000271014363"
            }],
            "version_external_identifier": 0,
            "receipt_creation_date_pst": "2017-02-06 00:57:55 America/Los_Angeles",
            "adam_id": 0,
            "receipt_type": "ProductionSandbox"
        },
        "latest_receipt_info": [{
                "purchase_date_ms": "1486371474000",
                "web_order_line_item_id": "1000000034281189",
                "original_purchase_date_ms": "1486371475000",
                "original_purchase_date": "2017-02-06 08:57:55 Etc/GMT",
                "expires_date_pst": "2017-02-06 01:00:54 America/Los_Angeles",
                "original_purchase_date_pst": "2017-02-06 00:57:55 America/Los_Angeles",
                "purchase_date_pst": "2017-02-06 00:57:54 America/Los_Angeles",
                "expires_date_ms": "1486371654000",
                "expires_date": "2017-02-06 09:00:54 Etc/GMT",
                "original_transaction_id": "1000000271014363",
                "purchase_date": "2017-02-06 08:57:54 Etc/GMT",
                "quantity": "1",
                "is_trial_period": "true",
                "product_id": "com.yourcompany.yourapp",
                "transaction_id": "1000000271014363"
            }, {
                "purchase_date_ms": "1486371719000",
                "web_order_line_item_id": "1000000034281190",
                "original_purchase_date_ms": "1486371720000",
                "original_purchase_date": "2017-02-06 09:02:00 Etc/GMT",
                "expires_date_pst": "2017-02-06 01:06:59 America/Los_Angeles",
                "original_purchase_date_pst": "2017-02-06 01:02:00 America/Los_Angeles",
                "purchase_date_pst": "2017-02-06 01:01:59 America/Los_Angeles",
                "expires_date_ms": "1486372019000",
                "expires_date": "2017-02-06 09:06:59 Etc/GMT",
                "original_transaction_id": "1000000271014363",
                "purchase_date": "2017-02-06 09:01:59 Etc/GMT",
                "quantity": "1",
                "is_trial_period": "false",
                "product_id": "com.yourcompany.yourapp",
                "transaction_id": "1000000271016119"
            }],
        "environment": "Sandbox"
    }


8. App Store, asyncio version (available in the inapppy.asyncio package)
========================================================================
.. code:: python

    from inapppy import InAppPyValidationError
    from inapppy.asyncio import AppStoreValidator


    bundle_id = 'com.yourcompany.yourapp'
    auto_retry_wrong_env_request=False # if True, automatically query sandbox endpoint if
                                       # validation fails on production endpoint
    validator = AppStoreValidator(bundle_id, auto_retry_wrong_env_request=auto_retry_wrong_env_request)

    try:
        exclude_old_transactions=False # if True, include only the latest renewal transaction
        validation_result = await validator.validate('receipt', 'optional-shared-secret', exclude_old_transactions=exclude_old_transactions)
    except InAppPyValidationError as ex:
        # handle validation error
        response_from_apple = ex.raw_response  # contains actual response from AppStore service.
        pass



9. Development
==============

.. code:: bash

    # run checks and tests
    tox

    # setup project
    make setup

    # check for lint errors
    make lint

    # run tests
    make test

    # run black
    make black

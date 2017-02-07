InAppPy
=======
|travis| |pypi|

.. |travis| image:: https://travis-ci.org/dotpot/InAppPy.svg?branch=master
    :target: https://travis-ci.org/dotpot/InAppPy
.. |pypi| image:: https://badge.fury.io/py/inapppy.svg
    :target: https://badge.fury.io/py/inapppy

In-app purchase validation library for Apple AppStore and GooglePlay.

Installation
============
::

    pip install inapppy

Usage
=====

Currently inapppy supports Google Play and App Store receipts validation.

Google Play (validates `receipt` against provided `signature` using RSA):
-------------------------------------------------------------------------
.. code:: python

    from inapppy import GooglePlayValidator, InAppPyValidationError


    bundle_id = 'com.yourcompany.yourapp'
    api_key = 'API key from the developer console'
    validator = GooglePlayValidator(bundle_id, api_key)

    try:
        validation_result = validator.validate('receipt', 'signature')
    except InAppPyValidationError:
        # handle validation error
        pass

App Store (validates `receipt` using optional `shared-secret` against iTunes service):
--------------------------------------------------------------------------------------
.. code:: python

    from inapppy import AppStoreValidator, InAppPyValidationError


    bundle_id = 'com.yourcompany.yourapp'
    validator = AppStoreValidator(bundle_id)

    try:
        validation_result = validator.validate('receipt', 'optional-shared-secret')
    except InAppPyValidationError as ex:
        # handle validation error
        response_from_apple = ex.raw_response  # contains actual response from AppStore service.
        pass

App Store Response (`validation_result` / `raw_response`) Sample:
-----------------------------------------------------------------
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

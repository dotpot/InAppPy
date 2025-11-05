InAppPy
=======
|ci| |pypi| |downloads|

.. |ci| image:: https://github.com/dotpot/InAppPy/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/dotpot/InAppPy/actions/workflows/ci.yml
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

   - Setting up Google Service Account Credentials
   - Usage Example (with file path)
   - Usage Example (with credentials dictionary)

5. Google Play (verification with result)
6. Google Play (consuming products)
7. App Store (`receipt` + using optional `shared-secret`)
8. App Store Response (`validation_result` / `raw_response`) example
9. App Store, **asyncio** version (available in the inapppy.asyncio package)
10. Development
11. Donate


1. Introduction
===============

In-app purchase validation library for `Apple AppStore` and `GooglePlay` (`App Store` validator have **async** support!). Works on python3.6+

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


An additional example showing how to authenticate using dict credentials instead of loading from a file

.. code:: python

    import json
    from inapppy import GooglePlayValidator, InAppPyValidationError


    bundle_id = 'com.yourcompany.yourapp'
    # Avoid hard-coding credential data in your code. This is just an example. 
    api_credentials = json.loads('{'
                                 '   "type": "service_account",'
                                 '   "project_id": "xxxxxxx",'
                                 '   "private_key_id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",'
                                 '   "private_key": "-----BEGIN PRIVATE KEY-----\nXXXXXXXXXXXXXXXXXXXXXXXXXXXXX==\n-----END PRIVATE KEY-----\n",'
                                 '   "client_email": "XXXXXXXXX@XXXXXXXX.XXX",'
                                 '   "client_id": "XXXXXXXXXXXXXXXXXX",'
                                 '   "auth_uri": "https://accounts.google.com/o/oauth2/auth",'
                                 '   "token_uri": "https://oauth2.googleapis.com/token",'
                                 '   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",'
                                 '   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/XXXXXXXXXXXXXXXXX.iam.gserviceaccount.com"'
                                 ' }')
    validator = GooglePlayValidator(bundle_id, api_credentials)

    try:
        # receipt means `androidData` in result of purchase
        # signature means `signatureAndroid` in result of purchase
        validation_result = validator.validate('receipt', 'signature')
    except InAppPyValidationError:
        # handle validation error
        pass



4. Google Play verification
===========================

Setting up Google Service Account Credentials
----------------------------------------------

Before using Google Play verification, you need to set up a Google Service Account and obtain the credentials file. This section explains what ``GOOGLE_SERVICE_ACCOUNT_KEY_FILE`` is and how to obtain it.

**What is GOOGLE_SERVICE_ACCOUNT_KEY_FILE?**

``GOOGLE_SERVICE_ACCOUNT_KEY_FILE`` is a JSON file containing a service account's private key and credentials. This file authorizes your application to access the Google Play Developer API to verify in-app purchases and subscriptions.

The credentials can be provided in two ways:

1. **As a file path** (string): Path to the JSON key file downloaded from Google Cloud Console
2. **As a dictionary** (dict): The parsed JSON content of the key file

**How to obtain the Service Account Key File:**

1. **Link Google Cloud Project to Google Play Console**

   - Go to `Google Play Console <https://play.google.com/console>`_
   - Select your app
   - Navigate to **Settings → Developer account → API access**
   - If you haven't linked a project yet, click **Link** to create or link a Google Cloud project
   - Accept the terms and conditions

2. **Create a Service Account**

   - In the API access page, scroll to **Service accounts**
   - Click **Create new service account** or **Learn how to create service accounts** (this will take you to Google Cloud Console)
   - In Google Cloud Console:

     - Go to **IAM & Admin → Service Accounts**
     - Click **+ CREATE SERVICE ACCOUNT**
     - Enter a name (e.g., "InAppPy Validator") and description
     - Click **CREATE AND CONTINUE**
     - Skip granting roles (not needed for this step)
     - Click **DONE**

3. **Grant Permissions in Google Play Console**

   - Return to Google Play Console → **Settings → Developer account → API access**
   - Find your newly created service account in the list
   - Click **Grant access**
   - Under **App permissions**, select your app
   - Under **Account permissions**, enable:

     - **View financial data** (for viewing purchase/subscription info)
     - **Manage orders and subscriptions** (if you need to consume products or manage subscriptions)

   - Click **Invite user** and then **Send invitation**

4. **Download the JSON Key File**

   - Go back to **Google Cloud Console → IAM & Admin → Service Accounts**
   - Click on your service account email
   - Go to the **KEYS** tab
   - Click **ADD KEY → Create new key**
   - Select **JSON** as the key type
   - Click **CREATE**
   - The JSON key file will be automatically downloaded
   - **IMPORTANT**: Store this file securely! It contains a private key and cannot be recovered if lost

5. **Important Notes**

   - The JSON key file should contain fields like: ``type``, ``project_id``, ``private_key_id``, ``private_key``, ``client_email``, etc.
   - Keep this file secure and never commit it to version control
   - In some cases, you may need to create at least one product in your Google Play Console before the API access works properly
   - It may take a few minutes for permissions to propagate after granting access

**Example JSON key file structure:**

.. code:: json

    {
      "type": "service_account",
      "project_id": "your-project-id",
      "private_key_id": "a1b2c3d4e5f6...",
      "private_key": "-----BEGIN PRIVATE KEY-----\nYourPrivateKeyHere\n-----END PRIVATE KEY-----\n",
      "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
      "client_id": "123456789",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
    }

Usage Example (with file path)
-------------------------------

.. code:: python

    from inapppy import GooglePlayVerifier, errors


    def google_validator(receipt):
        """
        Accepts receipt, validates in Google.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']

        # Pass the path to your service account JSON key file
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            '/path/to/your-service-account-key.json',  # Path to the JSON key file
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


Usage Example (with credentials dictionary)
--------------------------------------------

.. code:: python

    import json
    from inapppy import GooglePlayVerifier, errors


    def google_validator(receipt):
        """
        Accepts receipt, validates in Google using dict credentials.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']

        # Load credentials from environment variable or secure storage
        # NEVER hard-code credentials in your source code!
        credentials_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        credentials_dict = json.loads(credentials_json)

        # Pass the credentials as a dictionary
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            credentials_dict,  # Dictionary containing the JSON key data
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

**Note:** See section 4 for instructions on setting up ``GOOGLE_SERVICE_ACCOUNT_KEY_FILE``.

.. code:: python

    from inapppy import GooglePlayVerifier, errors


    def google_validator(receipt):
        """
        Accepts receipt, validates in Google.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']

        # Use the service account credentials (see section 4 for setup)
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            GOOGLE_SERVICE_ACCOUNT_KEY_FILE,  # Path to JSON key file or dict
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


6. Google Play (consuming products)
===================================
After validating a purchase, you can consume a one-time product to prevent refunds and allow the user to purchase it again.
This is a separate operation that should be called after verification to handle cases like power outages between validation and consumption.

**Note:** See section 4 for instructions on setting up ``GOOGLE_SERVICE_ACCOUNT_KEY_FILE``.

.. code:: python

    from inapppy import GooglePlayVerifier, errors


    def consume_purchase(receipt):
        """
        Consume a purchase after validation.
        """
        purchase_token = receipt['purchaseToken']
        product_sku = receipt['productId']

        # Use the service account credentials (see section 4 for setup)
        verifier = GooglePlayVerifier(
            GOOGLE_BUNDLE_ID,
            GOOGLE_SERVICE_ACCOUNT_KEY_FILE,  # Path to JSON key file or dict
        )

        try:
            # First verify the purchase
            verification_result = verifier.verify(
                purchase_token,
                product_sku,
                is_subscription=False
            )

            # Then consume it to prevent refunds
            consume_result = verifier.consume_product(
                purchase_token,
                product_sku
            )

            return {'success': True, 'consumed': True}
        except errors.GoogleError as exc:
            logging.error('Purchase consumption failed {}'.format(exc))
            return {'success': False, 'error': str(exc)}


**Note:** Only consumable products (one-time purchases) can be consumed. Subscriptions cannot be consumed.


7. App Store (validates `receipt` using optional `shared-secret` against iTunes service)
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



8. App Store Response (`validation_result` / `raw_response`) example
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


9. App Store, asyncio version (available in the inapppy.asyncio package)
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
        async with validator:  # Use async context manager to ensure proper session management
            validation_result = await validator.validate('receipt', 'optional-shared-secret', exclude_old_transactions=exclude_old_transactions)
    except InAppPyValidationError as ex:
        # handle validation error
        response_from_apple = ex.raw_response  # contains actual response from AppStore service.
        pass



10. Development
===============

Prerequisites
-------------

Install `uv <https://docs.astral.sh/uv/>`_ for fast Python package management:

.. code:: bash

    # macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

Setup and Testing
-----------------

.. code:: bash

    # Install development dependencies
    make dev

    # Run linting checks
    make lint

    # Format code with ruff
    make format

    # Run both lint and format checks
    make check

    # Run tests
    make test

    # Run tests with pytest directly
    uv run pytest -v

Available Make Commands
-----------------------

.. code:: bash

    make setup     # Install dependencies with uv
    make dev       # Install development dependencies with uv
    make clean     # Remove build artifacts
    make build     # Build distribution packages
    make release   # Upload to PyPI
    make test      # Run tests with pytest
    make lint      # Run ruff linting
    make format    # Format code with ruff
    make check     # Run lint and format check
    make install   # Install package in editable mode
    
11. Donate
==========
You can support development of this project by buying me a coffee ;)

+------+--------------------------------------------+
| Coin | Wallet 			            |
+======+============================================+
| EUR  | https://paypal.me/LukasSalkauskas          |
+------+--------------------------------------------+
| DOGE | DGjSG3T6g9h2k6iSku7mtKCynCpmwowpyN         |
+------+--------------------------------------------+
| BTC  | 1LZAiWmLYzZae4hq3ai9hFYD3e3qcwjDsU         |
+------+--------------------------------------------+
| ETH  | 0xD62245986345130edE10e4b545fF577Bd5BaE3E4 |
+------+--------------------------------------------+

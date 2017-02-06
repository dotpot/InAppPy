inapppy
=======

In-app purchase validator for Apple AppStore and GooglePlay.

Installation
============
::

    pip install inapppy

Usage
=====

Currently inapppy supports Google Play and App Store receipts validation.

Google Play:
------------
.. code:: python

    from inapppy import GooglePlayValidator, InAppValidationError


    bundle_id = 'com.yourcompany.yourapp'
    api_key = 'API key from the developer console'
    validator = GooglePlayValidator(bundle_id, api_key)

    try:
        validation_result = validator.validate('receipt', 'signature')
    except InAppValidationError:
        """ handle validation error """

App Store:
----------
.. code:: python

    from inapppy import AppStoreValidator, InAppValidationError


    bundle_id = 'com.yourcompany.yourapp'
    validator = AppStoreValidator(bundle_id)

    try:
        validation_result = validator.validate('receipt', 'optional-shared-secret')
    except InAppValidationError:
        """ handle validation error """

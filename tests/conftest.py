from pytest import fixture

from inapppy import AppStoreValidator


@fixture
def generic_error_message() -> str:
    return "error message"


@fixture
def generic_raw_response() -> dict:
    return {"foo": "bar"}


@fixture
def appstore_validator() -> AppStoreValidator:
    return AppStoreValidator()


@fixture
def appstore_validator_sandbox() -> AppStoreValidator:
    return AppStoreValidator(sandbox=True)


@fixture
def appstore_validator_auto_retry_on_sandbox() -> AppStoreValidator:
    return AppStoreValidator(auto_retry_wrong_env_request=True)

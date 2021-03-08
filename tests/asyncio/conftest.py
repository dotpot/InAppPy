from pytest import fixture

from inapppy.asyncio import AppStoreValidator


@fixture
def appstore_validator() -> AppStoreValidator:
    return AppStoreValidator()


@fixture
def appstore_validator_sandbox() -> AppStoreValidator:
    return AppStoreValidator(sandbox=True)


@fixture
def appstore_validator_auto_retry_on_sandbox() -> AppStoreValidator:
    return AppStoreValidator(auto_retry_wrong_env_request=True)

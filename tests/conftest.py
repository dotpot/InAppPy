from pytest import fixture


@fixture
def generic_error_message():
    return "error message"


@fixture
def generic_raw_response():
    return {"foo": "bar"}

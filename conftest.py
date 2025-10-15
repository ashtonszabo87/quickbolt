import pytest


def pytest_addoption(parser):
    parser.addoption("--test-debug", action="store", default=False)


@pytest.fixture
def test_debug(request):
    return request.config.getoption("--test-debug").lower() == "true"

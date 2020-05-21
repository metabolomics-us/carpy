import os

import pytest

from cisclient.client import CISClient


def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://dev-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = 'rDJfRW6ilG2WooOR72AaE3NqL4m23WvY6ub4FEoS'


@pytest.fixture()
def api_token():
    api_token = os.getenv('CIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the CIS api token in your env under CIS_API_TOKEN!"

    return {'x-api-key': api_token.strip()}


@pytest.fixture
def cis_cli():
    return CISClient(os.getenv('CIS_URL'), os.getenv('CIS_API_TOKEN'))

@pytest.fixture()
def library_test_name():
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture()
def splash_test_name():
    return ("splash10-0002-0309000000-2369135f42cccebdb7f0","soqe[M+H][M+NH4] | QExactive | test | positive")

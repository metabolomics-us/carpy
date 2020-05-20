import os

import pytest

from cisclient.client import CISClient


def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://test-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = '9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'


@pytest.fixture()
def api_token():
    api_token = os.getenv('CIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the CIS api token in your env under CIS_API_TOKEN!"

    return {'x-api-key': api_token.strip()}


@pytest.fixture
def cis_cli():
    return CISClient(os.getenv('CIS_URL'), os.getenv('CIS_API_TOKEN'))

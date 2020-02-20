import os

import pytest
from stasis_client.client import StasisClient


def pytest_generate_tests(metafunc):
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_BUCKET'] = 'wcmc-data-stasis-result-test'
    os.environ['STASIS_API_TOKEN'] = '9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'


@pytest.fixture
def stasis():
    return StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'), os.getenv('STASIS_BUCKET'))


@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"
    return {'x-api-key': api_token.strip()}

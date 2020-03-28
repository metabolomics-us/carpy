import os

import pytest
from stasis_client.client import StasisClient


def pytest_generate_tests(metafunc):
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_API_TOKEN'] = '9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'


@pytest.fixture
def stasis():
    client = StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'))

    print(f"raw:  {client.get_raw_bucket()}")
    print(f"json: {client.get_processed_bucket()}")
    print(f"zip:  {client.get_aggregated_bucket()}")
    return client


@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"
    return {'x-api-key': api_token.strip()}

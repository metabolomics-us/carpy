import os
from datetime import time

import pytest

from stasis_client.client import StasisClient

sample_time = time()


def pytest_generate_tests(metafunc):
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_API_TOKEN'] = '9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi'

@pytest.fixture
def sample(name: str = 'test'):
    data = {
        'sample': '123-{}-{}'.format(name, sample_time),
        'experiment': f'mySecretExp_{123}',
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',
            'name': 'some name',
            'method': 'gcms'
        },
        'processing': {
            'method': 'gcms'
        },
        'metadata': {
            'class': '12345',
            'species': 'alien',
            'organ': 'honker'
        },
        'userdata': {
            'label': 'filexxx',
            'comment': ''
        }
    }
    return data



@pytest.fixture()
def api_token():
    api_token = os.getenv('STASIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the stasis api token in your env under STASIS_API_TOKEN!"

    print(api_token)
    return {'x-api-key': api_token.strip()}
@pytest.fixture
def stasis_cli():
    return StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'))

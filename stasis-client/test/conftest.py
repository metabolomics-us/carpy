import os
from datetime import time

import pytest

from stasis_client.client import StasisClient

sample_time = time()


def pytest_generate_tests(metafunc):
    os.environ['STASIS_BUCKET'] = 'wcmc-data-stasis-result-test'
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_API_TOKEN'] = 'GUec9mh1jc6VFbudSzxfz8aIqdRiadqw6wWBzRCB'


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


@pytest.fixture
def stasis_cli():
    return StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'), os.getenv('STASIS_BUCKET'))

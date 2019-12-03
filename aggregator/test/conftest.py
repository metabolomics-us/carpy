import os

import pytest
from stasis_client.client import StasisClient


def pytest_generate_tests(metafunc):
    os.environ['STASIS_API_TOKEN'] = 'GUec9mh1jc6VFbudSzxfz8aIqdRiadqw6wWBzRCB'
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_BUCKET'] = 'wcmc-data-stasis-result-test'


@pytest.fixture
def stasis():
    return StasisClient(os.getenv('STASIS_URL'), os.getenv('STASIS_API_TOKEN'), os.getenv('STASIS_BUCKET'))

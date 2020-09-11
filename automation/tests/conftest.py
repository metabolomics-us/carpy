import os

import pytest
from stasis_client.client import StasisClient

from scheduler.scheduler import Scheduler


def pytest_generate_tests(metafunc):
    os.environ['TEST_STASIS_API_TOKEN'] = ''


@pytest.fixture()
def scheduler(config, stasis_cli):
    return Scheduler(config, stasis_cli)


@pytest.fixture()
def stasis_cli(stasis_token, stasis_url):
    return StasisClient(stasis_url, stasis_token)


@pytest.fixture()
def stasis_token():
    return "9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi"


@pytest.fixture()
def stasis_url():
    return "https://test-api.metabolomics.us/stasis"


@pytest.fixture()
def config():
    return {'test': False,
            'experiment': {
                'name': 'new-test',
                'chromatography': [
                    {'method': 'teddy',
                     'instrument': '6530',
                     'column': 'test',
                     'ion_mode': 'positive',
                     'raw_files_list': 'samples-pos.csv',
                     'raw_files': []},
                    {'method': 'teddy',
                     'instrument': '6550',
                     'column': 'test',
                     'ion_mode': 'negative',
                     'raw_files_list': 'samples-neg.txt',
                     'raw_files': []}
                ],
                'metadata': {'species': 'human', 'organ': 'plasma'}
            },
            'create_tracking': False,
            'create_acquisition': True,
            'env': 'test',
            }


@pytest.fixture()
def data():
    return {
        'sample': 'test-file',
        'experiment': 'test',
        'acquisition': {
            'instrument': 'QExactive',
            'ionisation': 'positive',
            'method': 'hilic',
            'column': 'test'
        },
        'processing': {
            'method': 'hilic | QExactive | test | positive'
        },
        'metadata': {
            'class': 'plasma',
            'species': 'human',
            'organ': 'plasma'
        }
    }

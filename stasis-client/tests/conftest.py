import os
import uuid

import pytest

from stasis_client.client import StasisClient

SAMPLE_UUID = uuid.uuid1()


def pytest_generate_tests(metafunc):
    os.environ['STASIS_URL'] = 'https://test-api.metabolomics.us/stasis'
    os.environ['STASIS_API_TOKEN'] = 'lcb-master-293fef66165126eb11f38459da38b291'


@pytest.fixture
def sample(name: str = 'test'):
    data = {
        'sample': '123-{}-{}'.format(name, SAMPLE_UUID),
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
def sample_tracking_data(stasis_cli, sample):
    data = [
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "scheduled"
        },
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "deconvoluted"
        },
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "corrected"
        },
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "annotated"
        },
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "quantified"
        },
        {
            "fileHandle": "{}.mzml".format(sample['sample']),
            "value": "replaced"
        },
        {
            "fileHandle": "{}.mzml.json".format(sample['sample']),
            "value": "exported"
        }
    ]

    for x in data:
        stasis_cli.sample_state_update(state=x['value'], sample_name=sample['sample'], file_handle=x['fileHandle'])

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

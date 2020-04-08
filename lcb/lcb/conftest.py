import os

import pytest
import requests
from stasis_client.client import StasisClient

from lcb.evaluator import SampleEvaluator


@pytest.fixture
def stasis_token():
    return os.getenv('STASIS_API_TOKEN')


@pytest.fixture
def stasis_url():
    return os.getenv('STASIS_API_URL')


@pytest.fixture
def stasis_cli(stasis_token, stasis_url):
    return StasisClient(stasis_url, stasis_token)


@pytest.fixture
def sample_evaluator(stasis_cli):
    return SampleEvaluator(stasis=stasis_cli)


@pytest.fixture
def test_sample(stasis_cli):
    """
    defines a test sample we want to evaluate
    :param stasis_cli:
    :return:
    """
    sample = {
        "acquisition": {
            "instrument": "6530test",
            "ionization": "positive",
            "method": "test"
        },
        "experiment": "teddy",
        "id": "lc-test-experiment",
        "metadata": {
            "organ": "test-organ",
            "species": "test-species"
        },
        "processing": {
            "method": "test | 6530test | test | positive"
        },
        "sample": "lc-test-sample",
        "time": 1563299315754
    }

    stasis_cli.sample_acquisition_create(data=sample)

    return sample


@pytest.fixture
def test_sample_result(stasis_cli, test_sample, stasis_token, stasis_url):
    """
    defines a test sample result we want to evaluate
    :param stasis_cli:
    :return:
    """
    data = {
        'sample': test_sample['sample'],
        'injections': {
            'test_1': {
                'logid': '1234',
                'correction': {
                    'polynomial': 5,
                    'sampleUsed': 'test',
                    'curve': [
                        {
                            'x': 121.12,
                            'y': 121.2
                        },
                        {
                            'x': 123.12,
                            'y': 123.2
                        }
                    ]
                },
                'results': [
                    {
                        'target': {
                            'retentionIndex': 121.12,
                            'name': 'test',
                            'id': 'test_id',
                            'mass': 12.2
                        },
                        'annotation': {
                            'retentionIndex': 121.2,
                            'intensity': 10.0,
                            'replaced': False,
                            'mass': 12.2
                        }
                    },
                    {
                        'target': {
                            'retentionIndex': 123.12,
                            'name': 'test2',
                            'id': 'test_id2',
                            'mass': 132.12
                        },
                        'annotation': {
                            'retentionIndex': 123.2,
                            'intensity': 103.0,
                            'replaced': True,
                            'mass': 132.12
                        }
                    }
                ]
            }
        }
    }

    response = requests.post("{}/result".format(stasis_url), json=data,
                             headers={'x-api-key': stasis_token.strip()})
    assert 200 == response.status_code
    return data

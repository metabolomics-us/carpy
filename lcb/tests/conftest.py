import os
from time import sleep, time

import pytest
import requests

from cisclient.client import CISClient
from stasis_client.client import StasisClient

from lcb.job_evaluator import JobEvaluator
from lcb.sample_evaluator import SampleEvaluator


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
def compound(splash_test_name, cis_cli):
    library = splash_test_name[1]
    splash = splash_test_name[0]
    compound = cis_cli.get_compound(library=library, splash=splash)
    return compound

@pytest.fixture()
def compound_with_sim_hits(splash_test_name, cis_cli):
    library = splash_test_name[1]
    splash = "splash10-0002-0900000000-bc79c0a270a8057469b4"
    compound = cis_cli.get_compound(library=library, splash=splash)
    return compound

@pytest.fixture()
def compound_with_sim_hits2(splash_test_name, cis_cli):
    library = splash_test_name[1]
    splash = "splash10-0002-0900000000-bc79c0a270a8057469b4"
    compound = cis_cli.get_compound(library=library, splash=splash)
    return compound
@pytest.fixture()
def members(splash_test_name, cis_cli):
    library = splash_test_name[1]
    splash = splash_test_name[0]

    compound = cis_cli.get_compound(library=library, splash=splash)
    members = list(map(lambda member: cis_cli.get_compound(library=library, splash=member),
                       cis_cli.get_members(library=library, splash=splash)))

    return members


@pytest.fixture()
def splash_test_name():
    return ("splash10-01b9-0970000000-1a036ef46908812dc204", "soqe[M-H] | QExactive | test | negative")

@pytest.fixture
def stasis_token():
    return "9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi"


@pytest.fixture
def stasis_url():
    return "https://test-api.metabolomics.us/stasis"


@pytest.fixture
def stasis_cli(stasis_token, stasis_url):
    return StasisClient(stasis_url, stasis_token)


@pytest.fixture
def sample_evaluator(stasis_cli):
    return SampleEvaluator(stasis=stasis_cli)


@pytest.fixture
def job_evaluator(stasis_cli):
    return JobEvaluator(stasis=stasis_cli)


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
            "method": "teddy | 6530test | test | positive"
        },
        "sample": "lc-test-sample",
        "time": 1563299315754
    }

    stasis_cli.sample_acquisition_create(data=sample)

    return sample


@pytest.fixture()
def test_sample_tracking_data(stasis_cli, test_sample):
    data = [
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "scheduled"
        },
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "deconvoluted"
        },
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "corrected"
        },
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "annotated"
        },
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "quantified"
        },
        {
            "fileHandle": "{}.mzml".format(test_sample['sample']),
            "value": "replaced"
        },
        {
            "fileHandle": "{}.mzml.json".format(test_sample['sample']),
            "value": "exported"
        }
    ]

    for x in data:
        stasis_cli.sample_state_update(state=x['value'], sample_name=test_sample['sample'], file_handle=x['fileHandle'])

    print("sample stored {} sleeping a bit now for the queue to catch up".format(test_sample))
    sleep(30)
    return data


@pytest.fixture
def test_sample_result(stasis_cli, test_sample, stasis_token, stasis_url):
    """
    defines a test sample result we want to evaluate
    :param stasis_cli:
    :return:
    """
    data = {
        'sample': "{}".format(test_sample['sample']),
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


@pytest.fixture()
def test_job_definition():
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "test | 6530test | test | positive",
        "samples": [
            "lc-test-sample"
        ],
        "profile": "carrot.lcms",

        "meta": {
            "tracking": [
                {
                    "state": "entered",
                },
                {
                    "state": "acquired",
                    "extension": "d"
                },
                {
                    "state": "converted",
                    "extension": "mzml"
                },

            ]
        }

    }

    return job


@pytest.fixture()
def test_job(stasis_cli, test_sample, test_job_definition):
    stasis_cli.store_job(job=test_job_definition)
    return test_job_definition
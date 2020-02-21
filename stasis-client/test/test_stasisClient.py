import os
from time import time

import requests


def test_sample_acquisition_create(stasis_cli, sample):
    data = sample
    result = stasis_cli.sample_acquisition_create(data)
    print(result)
    assert 200 == result.status_code

    result = stasis_cli.sample_acquisition_get(data['sample'])
    print(result)
    assert data['sample'] == result['sample']


def test_acquisition_get(stasis_cli):
    result = stasis_cli.sample_acquisition_get(f'test_1')
    metadata = {'class': '123456',
                'organ': 'tissue',
                'species': 'rat'}
    print(result)
    assert metadata == result.get('metadata')


def test_sample_state(stasis_cli, sample):
    result = stasis_cli.sample_state_update(sample['sample'], 'entered')

    print(result)
    assert 200 == result.status_code
    assert 'entered' == stasis_cli.sample_state(sample['sample'])[0]['value']


def test_sample_result(stasis_cli):
    result = stasis_cli.sample_result('lgvty_cells_pilot_2_NEG_50K_BR_01.json')

    print(result)
    assert result is not None
    assert 'lgvty_cells_pilot_2_NEG_50K_BR_01' == result['sample']


def test_inexistent_result(stasis_cli):
    result = stasis_cli.sample_result('blah.blah')
    print(result)
    assert 'Error' in result
    assert 'blah.blah' == result.get('filename')


def test_persist_inexistent_file(stasis_cli):
    if os.path.exists('stfu/blah.blah'):
        os.remove('stfu/blah.blah')

    result = stasis_cli.sample_result('blah.blah', 'stfu')
    print(result)
    assert result['Error'] is not None
    assert os.path.exists('stfu/blah.blah') is False


def test_get_url(stasis_cli):
    assert "https://test-api.metabolomics.us/stasis" == stasis_cli.get_url()


def test_get_states(stasis_cli):
    result = stasis_cli.get_states()

    print(result)
    assert result is not None
    assert len(result) == 13
    assert 'failed' in result


def test_sample_schedule(stasis_cli):
    result = stasis_cli.schedule_sample_for_computation(
        sample_name='lgvty_cells_pilot_2_NEG_50K_BR_01.json',
        env="test",
        method="test",
        profile="lcms")

    print(result)
    assert result is not None


def test_load_job_state(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B2a_TEDDYLipids_Neg_NIST001.mzml",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ.mzml",
            "B10A_SA8922_TeddyLipids_Pos_122WP.mzml"
        ],
        "profile": "carrot.lcms",
        "task_version": "164",
        "env": "test"
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/schedule", json=job, headers=api_token)

    data = stasis_cli.load_job_state(test_id)
    print(data)
    assert 'count' in data
    assert 'sample_states' in data
    assert 'job_state' in data
    assert 'job_info' in data


def test_load_job(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B2a_TEDDYLipids_Neg_NIST001.mzml",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ.mzml",
            "B10A_SA8922_TeddyLipids_Pos_122WP.mzml"
        ],
        "profile": "carrot.lcms",
        "task_version": "164",
        "env": "test"
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/schedule", json=job, headers=api_token)

    data = stasis_cli.load_job(test_id)
    print(data)

    assert len(data) == 3


def test_get_raw_bucket(stasis_cli, api_token):
    data = stasis_cli.get_raw_bucket()
    print(data)
    assert data == 'data-carrot'

def test_get_aggregated_bucket(stasis_cli, api_token):
    data = stasis_cli.get_aggregated_bucket()
    print(data)
    assert data == 'wcmc-data-stasis-agg-test'


def test_get_result_bucket(stasis_cli, api_token):
    data = stasis_cli.get_processed_bucket()
    print(data)
    assert data == 'wcmc-data-stasis-result-test'

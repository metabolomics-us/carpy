from time import time, sleep

import requests
from pytest import fail


def test_sample_acquisition_create(stasis_cli, sample):
    data = sample
    result = stasis_cli.sample_acquisition_create(data)
    print(result)
    assert 200 == result.status_code

    result = stasis_cli.sample_acquisition_get(data['sample'])
    print(result)
    assert data['sample'] == result['sample']


def test_acquisition_get_fail_not_found(stasis_cli):
    try:
        result = stasis_cli.sample_acquisition_get(f'test_1-{time()}')
        fail()
    except Exception as e:
        pass


def test_file_handle_by_state(stasis_cli, sample, sample_tracking_data):
    result = stasis_cli.file_handle_by_state(sample['sample'], 'exported')
    assert result == "{}.mzml.json".format(sample['sample'])
    result = stasis_cli.file_handle_by_state(sample['sample'], 'deconvoluted')
    assert result == "{}.mzml".format(sample['sample'])


def test_sample_state(stasis_cli, sample):
    result = stasis_cli.sample_state_update(sample['sample'], 'entered')

    print(result)
    assert 200 == result.status_code
    assert 'entered' == stasis_cli.sample_state(sample['sample'])[0]['value']


def test_inexistent_result(stasis_cli):
    try:
        result = stasis_cli.sample_result_as_json('blah.blah')
        fail()
    except Exception as e:
        pass


def test_get_url(stasis_cli):
    assert "https://test-api.metabolomics.us/stasis" == stasis_cli.get_url()


def test_get_states(stasis_cli):
    result = stasis_cli.get_states()

    print(result)
    assert result is not None
    assert len(result) == 17
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
            "B2a_TEDDYLipids_Neg_NIST001",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ",
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
        "env": "test"
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

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
            "B2a_TEDDYLipids_Neg_NIST001",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ",
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
        "env": "test"
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    data = stasis_cli.load_job(test_id)
    print(data)

    assert len(data) == 3


def test_get_raw_bucket(stasis_cli, api_token):
    data = stasis_cli.get_raw_bucket()
    print(data)
    assert data == 'wcmc-data-stasis-raw-test'


def test_get_aggregated_bucket(stasis_cli, api_token):
    data = stasis_cli.get_aggregated_bucket()
    print(data)
    assert data == 'wcmc-data-stasis-agg-test'


def test_get_result_bucket(stasis_cli, api_token):
    data = stasis_cli.get_processed_bucket()
    print(data)
    assert data == 'wcmc-data-stasis-result-test'


def test_download_result_is_none(stasis_cli, api_token):
    data = stasis_cli.download_job_result("i_do_not_exist")

    assert data is None


def test_download_result(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
        "env": "test"
    }

    stasis_cli.store_job(job)

    assert stasis_cli.load_job_state(test_id)['job_state'] == "entered"

    stasis_cli.schedule_job(test_id)
    origin = time()
    duration = 0
    while duration < 90000:
        state = stasis_cli.load_job_state(test_id)['job_state']
        print(f"current state for job {test_id} is {state} and duration is {duration}")
        if state == 'aggregated':
            break

        sleep(10)
        duration = time() - origin

    # side test to ensure results are generated and can be downloaded
    stasis_cli.sample_result_as_json('B10A_SA8922_TeddyLipids_Pos_122WP')

    content = stasis_cli.download_job_result(test_id)

    assert content is not None
    print(content)

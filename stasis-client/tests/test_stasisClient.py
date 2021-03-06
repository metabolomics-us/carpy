from time import time, sleep

import pytest
import requests
from pytest import fail


def test_get_minix_id(stasis_cli):
    result = stasis_cli.get_minix_experiment("493881")
    print(result)
    assert result is not None


@pytest.mark.parametrize("sample_count", [5, 10, 50])
def test_store_job_sizes(sample_count, stasis_cli):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
    }

    samples = []
    for x in range(0, sample_count):
        samples.append(f"test_sample_{x}")

    job['samples'] = samples

    stasis_cli.store_job(job, enable_progress_bar=True)

    result = stasis_cli.load_job(test_id)

    assert len(result) == sample_count

    result = stasis_cli.load_job_state(test_id)

    print(result)

    stasis_cli.set_job_state(test_id, "failed")

    result = stasis_cli.load_job_state(test_id)

    assert result['job_state'] == "failed"


def test_store_job_with_class(stasis_cli):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",

        "samples": [
            "sample_1",
            "sample_2",
            "sample_3",
            "sample_4",
            "sample_5",
            "sample_6",
        ],

        "meta": {
            "tracking": [
                {
                    "state": "entered"
                },
                {
                    "state": "acquired",
                    "extension": "d"
                },
                {
                    "state": "converted",
                    "extension": "mzml"
                }
            ]
        },
        "classes": [
            {
                "name": "a",
                "organ": "test",
                "species": "human_test",
                "samples": [
                    "sample_1",
                    "sample_2",
                    "sample_3"
                ]
            },
            {
                "name": "b",
                "organ": "test_2",
                "species": "human_test_2",
                "samples": [
                    "sample_4",
                    "sample_5",
                    "sample_6"
                ]
            }

        ]
    }

    stored_samples = stasis_cli.store_job(job, enable_progress_bar=True)

    assert stored_samples == 6
    result1 = stasis_cli.sample_acquisition_get("sample_1")
    result2 = stasis_cli.sample_acquisition_get("sample_2")
    result3 = stasis_cli.sample_acquisition_get("sample_3")
    result4 = stasis_cli.sample_acquisition_get("sample_4")
    result5 = stasis_cli.sample_acquisition_get("sample_5")
    result6 = stasis_cli.sample_acquisition_get("sample_6")

    assert result1['metadata']['organ'] == 'test'
    assert result1['metadata']['species'] == 'human_test'
    assert result1['metadata']['class'] == 'a'

    assert result2['metadata']['organ'] == 'test'
    assert result2['metadata']['species'] == 'human_test'
    assert result2['metadata']['class'] == 'a'

    assert result3['metadata']['organ'] == 'test'
    assert result3['metadata']['species'] == 'human_test'
    assert result3['metadata']['class'] == 'a'

    assert result4['metadata']['organ'] == 'test_2'
    assert result4['metadata']['species'] == 'human_test_2'
    assert result4['metadata']['class'] == 'b'

    assert result5['metadata']['organ'] == 'test_2'
    assert result5['metadata']['species'] == 'human_test_2'
    assert result5['metadata']['class'] == 'b'

    assert result6['metadata']['organ'] == 'test_2'
    assert result6['metadata']['species'] == 'human_test_2'
    assert result6['metadata']['class'] == 'b'

    print(result1)


@pytest.mark.parametrize("sample_count", [5, 10, 50])
def test_overwrite_job_sizes(sample_count, stasis_cli):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
    }

    samples = []
    for x in range(0, sample_count):
        samples.append(f"test_sample_{x}")

    job['samples'] = samples
    stasis_cli.store_job(job, enable_progress_bar=True)
    result = stasis_cli.load_job(test_id)

    assert len(result) == sample_count

    result = stasis_cli.load_job_state(test_id)

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
    }

    samples = []
    for x in range(0, sample_count - 2):
        samples.append(f"test_sample_{x}_2")

    job['samples'] = samples
    stored_samples = stasis_cli.store_job(job, enable_progress_bar=True)
    assert stored_samples == sample_count - 2
    result = stasis_cli.load_job(test_id)

    assert len(result) == sample_count - 2

    result = stasis_cli.load_job_state(test_id)

    print(result)


def test_schedule_queue(stasis_cli):
    queue = stasis_cli.schedule_queue()

    assert 'StasisScheduleQueue-test_FARGATE' in queue
    pass


@pytest.mark.parametrize("sample_count", [50, 100, 300])
def test_schedule_job_sizes(sample_count, stasis_cli):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
        "resource": "DUMP"  # <== we don't actually want to process it and just push it into the dump queue!!!
    }

    samples = []
    for x in range(0, sample_count):
        samples.append(f"test_sample_{x}")

    job['samples'] = samples

    stored_samples = stasis_cli.store_job(job, enable_progress_bar=True)

    assert stored_samples == sample_count
    stasis_cli.schedule_job(job['id'])

    print("requesting job to be scheduled")
    stasis_cli.schedule_job(test_id)
    origin = time()
    duration = 0

    print("waiting for status update, the job needs to be SCHEDULED or FAILED at some stage")
    while duration < 1200000:
        try:
            state = stasis_cli.load_job_state(test_id)['job_state']
            print(f"current state for job {test_id} is {state} and duration is {duration}")
            if state == "scheduled":
                break
            if state == "failed":
                fail()
                break

            sleep(10)
            duration = time() - origin
        except Exception as e:
            print(str(e))
            pass


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
    assert len(result) == 19
    assert 'failed' in result


def test_schedule_steac(stasis_cli):
    result = stasis_cli.schedule_steac("test")


def test_sample_schedule(stasis_cli):
    result = stasis_cli.schedule_sample_for_computation(
        sample_name='lgvty_cells_pilot_2_NEG_50K_BR_01.json',
        method="test",
        profile="lcms")

    print(result)
    assert result is not None


def test_load_job_state(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    for x in [
        "B2a_TEDDYLipids_Neg_NIST001",
        "B10A_SA8931_TeddyLipids_Pos_14TCZ",
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]:
        requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json={
            "sample": x,
            "job": test_id
        }, headers=api_token)

    data = stasis_cli.load_job_state(test_id)
    print(data)
    assert 'job_state' in data
    assert 'job_info' in data


def test_load_job(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "profile": "carrot.lcms",
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    for x in [
        "B2a_TEDDYLipids_Neg_NIST001",
        "B10A_SA8931_TeddyLipids_Pos_14TCZ",
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]:
        requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json={
            "sample": x,
            "job": test_id
        }, headers=api_token)
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


def test_download_processed_sample_result_as_json(stasis_cli, api_token):
    data = stasis_cli.sample_result_as_json("B10A_SA8922_TeddyLipids_Pos_122WP")

    assert data is not None

    print(data)


def test_download_result(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
    }

    stasis_cli.store_job(job)

    assert stasis_cli.load_job_state(test_id)['job_state'] == "entered"

    stasis_cli.schedule_job(test_id)
    origin = time()
    duration = 0
    while duration < 1200000:
        try:
            state = stasis_cli.load_job_state(test_id)['job_state']
            print(f"current state for job {test_id} is {state} and duration is {duration}")
            if state == 'aggregated_and_uploaded':
                break
            elif state == 'failed':
                raise AssertionError("oh noes we failed!!!!")

            sleep(30)
            duration = time() - origin
        except AssertionError as e:
            raise e
        except Exception as e:
            pass

    # side test to ensure results are generated and can be downloaded
    stasis_cli.sample_result_as_json('B10A_SA8922_TeddyLipids_Pos_122WP')

    content = stasis_cli.download_job_result(test_id)

    assert content is not None
    print(content)


@pytest.mark.parametrize("sample_count", [10])
def test_schedule_force_sync(sample_count, stasis_cli):
    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",

        "profile": "carrot.lcms",
        "resource": "DUMP"  # <== we don't actually want to process it and just push it into the dump queue!!!
    }

    samples = []
    for x in range(0, sample_count):
        samples.append(f"test_sample_{x}")

    job['samples'] = samples

    stasis_cli.store_job(job, enable_progress_bar=True)
    stasis_cli.schedule_job(job['id'])

    print("requesting job to be scheduled")
    stasis_cli.schedule_job(test_id)
    origin = time()
    duration = 0

    print("waiting for status update, the job needs to be SCHEDULED or FAILED at some stage")
    while duration < 1200000:
        try:
            print(stasis_cli.force_sync(test_id))
            state = stasis_cli.load_job_state(test_id)['job_state']
            print(f"current state for job {test_id} is {state} and duration is {duration}")
            if state == "scheduled":
                break
            if state == "failed":
                fail()
                break

            sleep(10)
            duration = time() - origin
        except Exception as e:
            print(str(e))
            pass

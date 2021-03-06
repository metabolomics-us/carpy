import json
from time import time, sleep

import requests
from pytest import fail

from integrationTests.stasis.acquisition.test_acquisition import _upload_test_sample


def test_store_job_integration(api_token):
    """
    test the storing of a job
    :param api_token:
    :return:
    """

    test_id = "test_job_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "profile": "carrot.lcms",
    }

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    for sample in [
        "B2a_TEDDYLipids_Neg_NIST001",
        "B10A_SA8931_TeddyLipids_Pos_14TCZ",
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]:
        sample_to_submit = {
            "job": test_id,
            "sample": sample,
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
        response = requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json=sample_to_submit,
                                 headers=api_token)
    assert response.status_code == 200


def test_schedule_job_integration_failed(api_token):
    """
    test the storing of a job
    :param api_token:
    :return:
    """

    test_id = "test_job_{}".format(time())

    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 404


def test_job_result_not_finished(api_token):
    """
    tests for a job which doesn't exist yet
    :param api_token:
    :return:
    """

    test_id = "test_job_i_do_not_finish_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "samples": [
            "B2a_TEDDYLipids_Neg_NIST001",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ",
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ],
        "profile": "carrot.lcms",
        "task_version": "164",
        "notify": [
            "wohlgemuth@ucdavis.edu",
            "berlinguyinca@gmail.com"
        ]
    }

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 404


def test_job_result_file_not_exist(api_token):
    """
    tests for a job which doesn't exist yet
    :param api_token:
    :return:
    """

    test_id = "test_job_i_do_not_exist_{}".format(time())

    print(test_id)
    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                             headers=api_token)

    assert response.status_code == 503


def test_job_result_not_exist(api_token):
    """
    tests for a job which doesn't exist yet
    :param api_token:
    :return:
    """

    test_id = "test_job_i_do_not_exist_{}".format(time())

    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 404


def test_schedule_job_integration(api_token):
    """
    test the scheduling of a job
    :param api_token:
    :return:
    """

    test_id = "test_job_{}".format(time())
    samples = [
        "B2a_TEDDYLipids_Neg_NIST001",
        "B10A_SA8931_TeddyLipids_Pos_14TCZ",
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]
    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "profile": "carrot.lcms",
    }

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)
    assert response.status_code == 200
    # register required tracking data for this item
    for sample in samples:
        data = [
            {
                "value": "entered"
            },
            {
                "fileHandle": "{}.d".format(sample),
                "value": "acquired"
            },
            {
                "fileHandle": "{}.mzml".format(sample),
                "value": "converted"
            },
            {
                "fileHandle": "{}.mzml".format(sample),
                "value": "scheduled"
            },
        ]

        for x in data:
            send = {
                "sample": sample,
                "status": x['value'],

            }
            if 'fileHandle' in x:
                send['fileHandle'] = x['fileHandle']
            result = requests.post('https://test-api.metabolomics.us/stasis/tracking', json=send, headers=api_token)
            assert result.status_code == 200

    # store sample/job association
    for sample in samples:
        sample_to_submit = {
            "job": test_id,
            "sample": sample,
        }
        response = requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json=sample_to_submit,
                                 headers=api_token)
        assert response.status_code == 200
    # schedule it
    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 200
    origin = time()
    duration = 0
    exspectation_met = False

    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently
    while duration < 900 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print("current job state for {}".format(test_id))
        print(json.dumps(result, indent=4))
        if result['job_state'] == 'aggregated_and_uploaded':
            exspectation_met = True
            #           assert result['sample_states'].get('exported', 0) == 2
            #           assert result['sample_states'].get('failed', 0) == 1
            break
        if result['job_state'] == 'failed':
            fail("this job failed!")
        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    print("downloading the result now for {}".format(test_id)
          )
    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                             headers=api_token)

    assert response.status_code == 200

    print("get all the sample states, which should be all 'exported' for this job")

    response = requests.get("https://test-api.metabolomics.us/stasis/job/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 200

    content = json.loads(response.content)

    assert len(content) == 3

    for x in content:
        assert x['state'] in ('exported', 'failed')


def test_schedule_job_integration_no_metadata_single_sample(api_token):
    """
    test the scheduling of a job, which forcefully override the existing metadata
    :param api_token:
    :return:
    """

    test_id = "test_job_no_meta_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
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
    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    # store sample/job association
    for sample in [
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]:
        sample_to_submit = {
            "job": test_id,
            "sample": sample,
        }
        response = requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json=sample_to_submit,
                                 headers=api_token)
        assert response.status_code == 200
    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 200
    origin = time()
    duration = 0
    exspectation_met = False

    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently
    while duration < 900 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print(result)
        if result['job_state'] == 'aggregated_and_uploaded':
            exspectation_met = True
            break

        if result['job_state'] == 'failed':
            fail("this job failed!")
        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    print("downloading the result now for {}".format(test_id)
          )
    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                             headers=api_token)

    assert response.status_code == 200


def test_schedule_job_integration_no_metadata(api_token):
    """
    test the scheduling of a job, which forcefully override the existing metadata
    :param api_token:
    :return:
    """

    test_id = "test_job_no_meta_{}".format(time())

    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "profile": "carrot.lcms",

    }

    samples = [
        "B2a_TEDDYLipids_Neg_NIST001",
        "B10A_SA8931_TeddyLipids_Pos_14TCZ",
        "B10A_SA8922_TeddyLipids_Pos_122WP"
    ]
    # reset metadata to state entered for the given samples
    for sample in samples:
        send = {
            "sample": sample,
            "status": 'entered',

        }
        result = requests.post('https://test-api.metabolomics.us/stasis/tracking', json=send, headers=api_token)
        assert result.status_code == 200

        # ensure we only have state entered now for this sample
        response = requests.get('https://test-api.metabolomics.us/stasis/tracking/{}'.format(sample), headers=api_token)
        assert 200 == response.status_code
        content = response.json()
        assert len(content['status']) == 1
        assert content['status'][0]['value'] == "entered"
        assert 'fileHandle' not in content['status'][0]

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    assert response.status_code == 200

    # store sample associations
    for sample in samples:
        sample_to_submit = {
            "job": test_id,
            "sample": sample,
        }
        response = requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json=sample_to_submit,
                                 headers=api_token)
        assert response.status_code == 200
    # schedule it
    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    origin = time()
    duration = 0
    exspectation_met = False

    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently
    while duration < 900 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print(result)
        if result['job_state'] == 'aggregated_and_uploaded':
            exspectation_met = True
            #            assert result['sample_states']['exported'] == 2
            #            assert result['sample_states']['failed'] == 1
            break

        if result['job_state'] == 'failed':
            fail("this job failed!")
        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    print("downloading the result now for {}".format(test_id)
          )
    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                             headers=api_token)

    assert response.status_code == 200


def test_issue_FIEHNLAB_382(api_token):
    """
    https://wcmc.myjetbrains.com/youtrack/issue/FIEHNLAB-382
    these particular samples keep hanging
    :param api_token:
    :return:
    """

    # TODO register the same sample with a different experiment
    # to actually simulate this behavior

    test_id = "test_job_382_{}".format(time())

    job = {
        "id": test_id,
        "method": "soqe[M-H] | QExactive | test | negative",
        "profile": "carrot.lcms",

    }

    samples = [
        "SOP_Tissue_PoolMSMS_004_MX524916_negCSH_880_1700",
        "SOP_Tissue_PoolMSMS_003_MX524916_negCSH_800_880",
        "SOP_Tissue_PoolMSMS_002_MX524916_negCSH_700_800"
    ]
    # reset metadata to state entered for the given samples
    for sample in samples:
        send = {
            "sample": sample,
            "status": 'entered',

        }
        result = requests.post('https://test-api.metabolomics.us/stasis/tracking', json=send, headers=api_token)
        assert result.status_code == 200

        # ensure we only have state entered now for this sample
        response = requests.get('https://test-api.metabolomics.us/stasis/tracking/{}'.format(sample), headers=api_token)
        assert 200 == response.status_code
        content = response.json()
        assert len(content['status']) == 1
        assert content['status'][0]['value'] == "entered"
        assert 'fileHandle' not in content['status'][0]

    # associated samples with some different experument
    for x in range(0, 4):
        for y in samples:
            _upload_test_sample(samplename=y, api_token=api_token, samples=x, experiment="FIEHNLAB382_{}")

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    assert response.status_code == 200

    # store sample associations
    for sample in samples:
        sample_to_submit = {
            "job": test_id,
            "sample": sample,
        }
        response = requests.post("https://test-api.metabolomics.us/stasis/job/sample/store", json=sample_to_submit,
                                 headers=api_token)
        assert response.status_code == 200
    # schedule it
    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    origin = time()
    duration = 0
    exspectation_met = False

    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently
    while duration < 90000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print(result)
        if result['job_state'] == 'aggregated_and_uploaded':
            exspectation_met = True
            #            assert result['sample_states']['exported'] == 2
            #            assert result['sample_states']['failed'] == 1
            break

        if result['job_state'] == 'failed':
            # generate fail report here
            for sample in samples:
                response = requests.get('https://test-api.metabolomics.us/stasis/tracking/{}'.format(sample),
                                        headers=api_token)

                print(response.json())
            fail("this job failed!")
        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    print("downloading the result now for {}".format(test_id)
          )
    response = requests.head("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                             headers=api_token)

    assert response.status_code == 200

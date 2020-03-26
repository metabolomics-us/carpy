import json
from time import time, sleep

import requests

from stasis.jobs.states import States


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
        "samples": [
            "B2a_TEDDYLipids_Neg_NIST001.mzml",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ.mzml",
            "B10A_SA8922_TeddyLipids_Pos_122WP.mzml"
        ],
        "profile": "carrot.lcms",
        "task_version": "164",
        "env": "test",
        "notify": [
            "wohlgemuth@ucdavis.edu",
            "berlinguyinca@gmail.com"
        ]
    }

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

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


def test_schedule_job_integration(api_token):
    """
    test the scheduling of a job
    :param api_token:
    :return:
    """

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
        "env": "test",
        "notify": [
            "wohlgemuth@ucdavis.edu",
            "berlinguyinca@gmail.com"
        ]
    }

    # store it
    response = requests.post("https://test-api.metabolomics.us/stasis/job/store", json=job, headers=api_token)

    assert response.status_code == 200

    # schedule it
    response = requests.put("https://test-api.metabolomics.us/stasis/job/schedule/{}".format(test_id),
                            headers=api_token)

    print(response)
    assert response.status_code == 200
    assert json.loads(response.content)['job'] == test_id
    assert json.loads(response.content)['state'] == str(States.SCHEDULED)

    # check state of samples

    response = requests.get("https://test-api.metabolomics.us/stasis/job/{}".format(test_id), headers=api_token)

    assert response.status_code == 200
    job = json.loads(response.content)

    for x in job:
        assert x['state'] == 'scheduled'
        assert x['job'] == test_id

    # just check the response code from the server
    response = requests.get("https://test-api.metabolomics.us/stasis/schedule/cluster/tasks", headers=api_token)

    assert response.status_code == 200
    origin = time()
    duration = 0
    exspectation_met = False
    while duration < 90000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print(result)
        if result['job_state'] == 'aggregation_scheduled':
            exspectation_met = True
            assert result['sample_states']['processed'] == 2
            assert result['sample_states']['failed'] == 1
            break

        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    origin = time()
    duration = 0
    exspectation_met = False
    print("job is in the aggregating stage")
    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently
    while duration < 90000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        print(result)
        if result['job_state'] == 'aggregated':
            exspectation_met = True
            assert result['sample_states']['processed'] == 2
            assert result['sample_states']['failed'] == 1
            break

        sleep(10)
        duration = time() - origin

    assert exspectation_met is True

    print("downloading the result now"
          )
    response = requests.get("https://test-api.metabolomics.us/stasis/job/result/{}".format(test_id),
                            headers=api_token)

    assert response.status_code == 200

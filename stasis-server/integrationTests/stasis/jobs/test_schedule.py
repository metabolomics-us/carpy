import json
from time import time, sleep

import requests

from stasis.jobs.states import States


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
        "env": "test"
    }

    response = requests.post("https://test-api.metabolomics.us/stasis/job/schedule", json=job, headers=api_token)

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

    # watch the state of the job until it's in state processing
    # processing means at least one sample needs to have the state processed
    origin = time()
    duration = 0
    exspectation_met = False
    while duration < 90000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}/true".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)
        print(result)
        if result['job_state'] == str(States.PROCESSING):
            print(result)
            assert 'processing' in result['sample_states']
            exspectation_met = True
            break

        sleep(1)
        duration = time() - origin

    assert exspectation_met is True

    print("job is in the processing stage")
    # watch the state of the job until it's processed
    # we are exspecting the following states
    # 1 x failed, since it's a negative sample with a positive library
    # 2 x processed
    # this is only here to check the state of a job and should
    # be called infrequently
    # DO NOT USE TRUE in clients as command, very expensive call!
    origin = time()
    duration = 0
    exspectation_met = False
    while duration < 90000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}/true".format(test_id),
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

    print("job is in the aggregating stage")
    # wait until the job is in state aggregated
    # fargate should automatically start and process this task for us
    # this should be called infrequently

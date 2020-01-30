import json
from time import time, sleep

import requests

from stasis.jobs.states import States

apiUrl = "https://test-api.metabolomics.us/stasis/job/schedule"


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

    response = requests.post(apiUrl, json=job, headers=api_token)

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

    response = requests.get("https://test-api.metabolomics.us/stasis/schedule/cluster/tasks", headers=api_token)

    assert response.status_code == 200

    # watch the state of the job until it's processed
    # we are exspecting the following states
    # 1 x failed, since it's a negative sample with a positive library
    # 2 x processed
    origin = time()
    duration = 0
    result = None
    exspectation_met = False
    while duration < 900000 and exspectation_met is False:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        result = json.loads(response.content)

        if result['job_state'] == 'aggregation_scheduled':
            exspectation_met = True
            assert result['sample_states']['processed'] == 2
            assert result['sample_states']['failed'] == 1
            break

        print(result)
        sleep(10)
        duration = time() - origin

    assert result is not None
    assert exspectation_met is True

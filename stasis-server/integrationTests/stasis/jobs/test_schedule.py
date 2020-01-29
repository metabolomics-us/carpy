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
            "B2a_TEDDYLipids_Neg_NIST001.mzml"
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
    while True:
        response = requests.get("https://test-api.metabolomics.us/stasis/job/status/{}".format(test_id),
                                headers=api_token)
        print(response.content)
        sleep(10)
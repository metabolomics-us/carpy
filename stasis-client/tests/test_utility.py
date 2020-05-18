from collections import Counter
from time import time

from stasis_client.utility import Utility


def test_state_distribution(stasis_cli, api_token):
    test_id = "test_job_{}".format(time())
    job = {
        "id": test_id,
        "method": "teddy | 6530 | test | positive",
        "profile": "carrot.lcms",
        "samples": [
            "B2a_TEDDYLipids_Neg_NIST001",
            "B10A_SA8931_TeddyLipids_Pos_14TCZ",
            "B10A_SA8922_TeddyLipids_Pos_122WP"
        ]
    }

    stasis_cli.store_job(job)

    utilities = Utility(client=stasis_cli)

    result: Counter = utilities.state_distribution(test_id)

    assert len(result.keys()) == 1

    stasis_cli.sample_state_update(sample_name="B2a_TEDDYLipids_Neg_NIST001", state='exported', file_handle=".d")

    result: Counter = utilities.state_distribution(test_id)

    assert len(result.keys()) == 2

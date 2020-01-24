import requests

apiUrl = "https://test-api.metabolomics.us/stasis/job/schedule"


def test_schedule_job_integration(api_token):
    """
    test the scheduling of a job
    :param api_token:
    :return:
    """

    job = {
        "id": "test_job",
        "method": "",
        "samples": [
            "abc_12345",
            "abd_12345",
            "abe_12345",
            "abf_12345",
            "abg_12345",
            "abh_12345",
            "abi_12345",
            "abj_12345",
            "abk_12345",
            "abl_12345",
            "abm_12345",
            "abn_12345",
            "abo_12345",
            "abp_12345",
            "abq_12345",
            "abr_12345",
            "abs_12345",
            "abt_12345",
            "abu_12345",
            "abx_12345",
            "aby_12345",
            "abz_12345"
        ],
        "profile": "lcms",
        "task_version": "1",
        "env": "test"
    }

    response = requests.post(apiUrl, json=job, headers=api_token)

    assert response.status_code == 200

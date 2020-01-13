import json

from stasis.jobs.schedule import schedule_job


def test_schedule_job(requireMocking):
    """
    tests the scheduling of a job
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
        ],
        "profile": "lcms",
        "task_version": "164",
        "env": "test"
    }

    schedule_job({'body': json.dumps(job)}, {})

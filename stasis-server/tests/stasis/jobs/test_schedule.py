import json

from stasis.jobs.schedule import schedule_job, monitor_jobs
from stasis.jobs.states import States
from stasis.schedule.schedule import monitor_queue
from stasis.tables import load_job_samples, get_tracked_state, get_job_state
from stasis.tracking import create


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
        "task_version": "1",
        "env": "test"
    }

    schedule_job({'body': json.dumps(job)}, {})

    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert v == 'scheduled'

    monitor_queue({}, {})

    # synchronize the job and sample tracking table
    monitor_jobs({}, {})

    assert get_job_state("test_job") == States.PROCESSING

    job = load_job_samples(job="test_job")
    assert len(job) == 5

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) == "scheduled"
        assert v == 'processing'

        # force stasis to be now  finish for this sample. We pretend it was calculated....
        response = create.create({'body': json.dumps({'sample': k, 'status': 'finished'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    # all job items should be in state processed now
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert get_tracked_state(k) == "finished"
        assert v == 'processed'

    # we should now have an aggregation scheduled
    assert get_job_state("test_job") == States.AGGREGATION_SCHEDULED

    # simulate the receiving of an aggregation event

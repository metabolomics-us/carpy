import json
import math
import random

from stasis.jobs.schedule import schedule_job, monitor_jobs
from stasis.jobs.states import States
from stasis.schedule.schedule import monitor_processing_queue, MESSAGE_BUFFER
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

    schedule_job({'body': json.dumps(job)}, {})

    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert v == 'scheduled'

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue
    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_processing_queue({}, {})

    # synchronize the job and sample tracking table
    monitor_jobs({}, {})

    assert get_job_state("test_job") == States.SCHEDULED

    job = load_job_samples(job="test_job")
    assert len(job) == 22

    # at this stage all jobs should be scheduled
    for k, v in job.items():
        assert get_tracked_state(k) == "scheduled", "assertion failed for {} with state {}".format(k,v)
        assert v == 'scheduled'

        # force stasis to be now have some processing samples and some scheduled samples
        # to ensure that evaluation works correct
        new_state = random.choice(["scheduled", "processing"])
        response = create.create({'body': json.dumps({'sample': k, 'status': new_state})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    # the overal job state is currently processing
    assert get_job_state("test_job") == States.PROCESSING

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) in ["scheduled", "processing"]
        assert v in ['scheduled', 'processing']

        # force stasis that all samples have been finished
        response = create.create({'body': json.dumps({'sample': k, 'status': 'finished'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    # all job items should be in state finished on the stasis side and processed on the job side
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert get_tracked_state(k) == "finished"
        assert v == 'processed'

    # we should now have jobs in the state aggregation scheduled
    # this means the jobs should be in the aggregator queue
    # but not processed by fargate yet
    assert get_job_state("test_job") == States.AGGREGATION_SCHEDULED

    # simulate the receiving of an aggregation event
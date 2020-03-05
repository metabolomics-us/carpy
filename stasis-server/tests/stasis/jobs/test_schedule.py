import json
import math
import random

from stasis.jobs.schedule import schedule_job, monitor_jobs
from stasis.jobs.states import States
from stasis.schedule.schedule import monitor_queue, MESSAGE_BUFFER
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
            "abc_12345.mzml",
            "abd_12345.mzml",
            "abe_12345.mzml",
            "abf_1234.mzml",
            "abg_12345.mzml",
            "abh_12345.mzml",
            "abi_12345.mzml",
            "abj_12345.mzml",
            "abk_12345.mzml",
            "abl_12345.mzml",
            "abm_12345.mzml",
            "abn_12345.mzml",
            "abo_12345.mzml",
            "abp_12345.mzml",
            "abq_12345.mzml",
            "abr_12345.mzml",
            "abs_12345.mzml",
            "abt_12345.mzml",
            "abu_12345.mzml",
            "abx_12345.mzml",
            "aby_12345.mzml",
            "abz_12345.mzml"
        ],
        "profile": "lcms",
        "env": "test"
    }

    result = schedule_job({'body': json.dumps(job)}, {})

    assert json.loads(result['body'])['state'] == str(States.SCHEDULED)
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert v == 'scheduled'

        response = create.create({'body': json.dumps({'sample': k.split(".")[0], 'status': v})}, {})

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue
    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_queue({}, {})

    # synchronize the job and sample tracking table
    monitor_jobs({}, {})

    assert get_job_state("test_job") == States.SCHEDULED

    job = load_job_samples(job="test_job")
    assert len(job) == 22

    # at this stage all jobs should be scheduled
    for k, v in job.items():
        assert get_tracked_state(k) == "scheduled", "assertion failed for {} with state {}".format(k, v)
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

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue

    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_queue({}, {})

    # we should now have jobs in the state aggregation scheduled
    # this means the jobs should be in the aggregator queue
    # but not processed by fargate yet
    state = get_job_state("test_job")
    assert States.AGGREGATION_SCHEDULED == state

    # simulate the receiving of an aggregation event

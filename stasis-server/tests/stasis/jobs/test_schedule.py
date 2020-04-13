import json
import math
import random

import pytest
from jsonschema import ValidationError
from pytest import fail

from stasis.jobs.schedule import schedule_job, monitor_jobs, store_job
from stasis.jobs.states import States
from stasis.schedule.backend import Backend
from stasis.schedule.schedule import monitor_queue, MESSAGE_BUFFER
from stasis.tables import load_job_samples, get_tracked_state, get_job_state, get_job_config
from stasis.tracking import create


def test_store_job_fail_empty_id(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "",
        "method": "test",
        "samples": [
            "abc_12345.mzml",
        ],
        "profile": "dada",
        "env": "test"
    }

    try:
        result = store_job({'body': json.dumps(job)}, {})
        fail()
    except ValidationError:
        pass


def test_store_job_fail_empty_method(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "",
        "samples": [
            "abc_12345.mzml",
        ],
        "profile": "dadsad",
        "env": "test"
    }

    try:
        result = store_job({'body': json.dumps(job)}, {})
        fail()
    except ValidationError:
        pass


def test_store_job_fail_empty_env(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
        "samples": [
            "abc_12345.mzml",
        ],
        "profile": "test",
        "env": ""
    }

    try:
        result = store_job({'body': json.dumps(job)}, {})
        fail()
    except ValidationError:
        pass


def test_store_job_fail_empty_profile(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
        "samples": [
            "abc_12345.mzml",
        ],
        "profile": "",
        "env": "test"
    }

    try:
        result = store_job({'body': json.dumps(job)}, {})
        fail()
    except ValidationError:
        pass


def test_store_job_fails_no_samples(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
        "samples": [
        ],
        "profile": "lcms",
        "env": "test"
    }

    try:
        result = store_job({'body': json.dumps(job)}, {})
        fail()
    except ValidationError:
        pass


def test_store_job(requireMocking):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
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

    result = store_job({'body': json.dumps(job)}, {})

    # check result state
    assert json.loads(result['body'])['state'] == 'stored'

    # query actual db and check internal state
    assert get_job_state("stored_test_job") == States.STORED


def test_schedule_job_fails_no_job_stored(requireMocking):
    """
    tests the scheduling of a job
    """

    result = schedule_job({'pathParameters': {
        "job": "test_job"
    }}, {})

    assert result['statusCode'] == 404


@pytest.mark.parametrize("backend", [Backend.FARGATE, Backend.LOCAL])
def test_schedule_job(requireMocking, backend):
    """
    tests the scheduling of a job
    """

    job = {
        "id": "test_job",
        "method": "test",
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
        "env": "test",
        "resource": backend.value
    }

    store_job({'body': json.dumps(job)}, {})

    ##
    # check for the correct backend
    ##
    validate_backened(backend)

    # here we do the actual schedulign now
    result = schedule_job({'pathParameters': {
        "job": "test_job"
    }}, {})

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

    validate_backened(backend)
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

    validate_backened(backend)
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

    validate_backened(backend)
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

    validate_backened(backend)
    # we should now have jobs in the state aggregation scheduled
    # this means the jobs should be in the aggregator queue
    # but not processed by fargate yet
    state = get_job_state("test_job")
    assert States.AGGREGATION_SCHEDULED == state

    # simulate the receiving of an aggregation event

    validate_backened(backend)


def validate_backened(backend):
    job_config = get_job_config("test_job")
    assert job_config['resource'] == backend

import json
import math
import random

import pytest

from stasis.jobs.schedule import schedule_job, monitor_jobs, store_job, store_sample_for_job
from stasis.schedule.backend import Backend
from stasis.schedule.monitor import monitor_queue
from stasis.schedule.schedule import MESSAGE_BUFFER
from stasis.service.Status import *
from stasis.tables import load_job_samples, get_tracked_state, get_job_state, get_job_config, get_tracked_sample
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
            "abc_12345",
        ],
        "profile": "dada",
        "env": "test"
    }

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


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
            "abc_12345",
        ],
        "profile": "dadsad",
        "env": "test"
    }

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


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
            "abc_12345",
        ],
        "profile": "test",
        "env": ""
    }

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


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
            "abc_12345",
        ],
        "profile": "",
        "env": "test"
    }

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


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

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


def test_store_job(requireMocking, mocked_10_sample_job):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    # check result state
    assert mocked_10_sample_job['state'] == 'entered'

    # query actual db and check internal state
    assert get_job_state(mocked_10_sample_job['id']) == ENTERED


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

        "profile": "lcms",
        "env": "test",
        "resource": backend.value
    }

    store_job({'body': json.dumps(job)}, {})

    for x in [
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
    ]:
        result = store_sample_for_job({
            'body': json.dumps({
                'job': "test_job",
                'sample': x
            })
        }, {})

    assert result['statusCode'] == 200
    ##
    # check for the correct backend
    ##
    validate_backened(backend)

    # here we do the actual schedulign now
    result = schedule_job({'pathParameters': {
        "job": "test_job"
    }}, {})

    assert json.loads(result['body'])['state'] == SCHEDULED
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
    assert get_job_state("test_job") == SCHEDULED

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
    assert get_job_state("test_job") == PROCESSING

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) in ["scheduled", "processing"]
        assert v in ['scheduled', 'processing']

        # force stasis that all samples have been finished
        response = create.create({'body': json.dumps({'sample': k, 'status': 'exported'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    validate_backened(backend)
    # all job items should be in state finished on the stasis side and processed on the job side
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert get_tracked_state(k) == "exported"

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

    validate_backened(backend)

    state = get_job_state("test_job")
    assert state in [AGGREGATING, AGGREGATING_SCHEDULED]  # kinda buggy
    # simulate the receiving of an aggregation event


@pytest.mark.parametrize("backend", [Backend.FARGATE, Backend.LOCAL])
def test_schedule_job_override_tracking_data(requireMocking, backend):
    """
    tests the scheduling of a job
    """

    job = {
        "id": "test_job",
        "method": "test",
        "samples": [
            "none_abc_12345",
            "none_abd_12345",
            "none_abe_12345",
            "none_abz_12345"
        ],
        "profile": "lcms",
        "env": "test",
        "resource": backend.value,
        "meta": {
            "tracking": [
                {
                    "state": "entered"
                },
                {
                    "state": "acquired",
                    "extension": "d"
                },
                {
                    "state": "converted",
                    "extension": "mzml"
                }
            ]
        }
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

    assert json.loads(result['body'])['state'] == SCHEDULED
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert v == 'scheduled'

        sample_state = get_tracked_sample(k)

        assert sample_state['status'][0]['value'] == 'entered'
        assert sample_state['status'][0].get('fileHandle', None) == None

        assert sample_state['status'][1]['value'] == 'acquired'
        assert sample_state['status'][1]['fileHandle'] == "{}.d".format(k)

        assert sample_state['status'][2]['value'] == 'converted'
        assert sample_state['status'][2]['fileHandle'] == "{}.mzml".format(k)

        assert sample_state['status'][3]['value'] == 'scheduling'
        assert sample_state['status'][3]['fileHandle'] == "{}.mzml".format(k)

        assert sample_state['status'][4]['value'] == 'scheduled'
        assert sample_state['status'][4]['fileHandle'] == "{}.mzml".format(k)

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue
    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_queue({}, {})

    # synchronize the job and sample tracking table
    monitor_jobs({}, {})

    validate_backened(backend)
    assert get_job_state("test_job") == SCHEDULED

    job = load_job_samples(job="test_job")
    assert len(job) == 4

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
    assert get_job_state("test_job") == PROCESSING

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) in ["scheduled", "processing"]
        assert v in ['scheduled', 'processing']

        # force stasis that all samples have been finished
        response = create.create({'body': json.dumps({'sample': k, 'status': 'exported'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    validate_backened(backend)
    # all job items should be in state finished on the stasis side and processed on the job side
    job = load_job_samples(job="test_job")
    for k, v in job.items():
        assert get_tracked_state(k) == "exported"

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

    validate_backened(backend)

    state = get_job_state("test_job")
    assert state in [AGGREGATING, AGGREGATING_SCHEDULED]  # kinda buggy

    # simulate the receiving of an aggregation event


def validate_backened(backend):
    job_config = get_job_config("test_job")
    assert job_config['resource'] == backend

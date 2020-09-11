import json
import math
import random

import pytest

from stasis.jobs.schedule import schedule_job, monitor_jobs, store_job, store_sample_for_job, schedule_job_from_queue
from stasis.schedule.backend import Backend
from stasis.schedule.monitor import monitor_queue
from stasis.schedule.schedule import _get_queue
from stasis.config import MESSAGE_BUFFER
from stasis.service.Status import *
from stasis.tables import load_job_samples_with_states, get_tracked_state, get_job_state, get_job_config, \
    get_tracked_sample
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
        "profile": "dada",
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
        "profile": "dadsad",
        "env": "test"
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
        "profile": "",
    }

    result = store_job({'body': json.dumps(job)}, {})
    assert result['statusCode'] == 503


@pytest.mark.parametrize("samples", [50, 500, 100, 500])
def test_store_job_many_samples(requireMocking, samples):
    """
    tests storing a job in the database
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
        "profile": "lcms",
    }

    result = store_job({'body': json.dumps(job)}, {})

    for x in range(1, samples):
        store_sample_for_job({'body': json.dumps({
            "job": job['id'],
            "sample": f"sample_{x}"}
        )}, {})

    assert result['statusCode'] == 200


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


def test_schedule_job(requireMocking, mocked_10_sample_job, backend):
    """
    tests the scheduling of a job
    """

    validate_backened(backend, mocked_10_sample_job)

    # here we do the actual schedulign now
    result = schedule_job({'pathParameters': {
        "job": mocked_10_sample_job['id']
    }}, {})

    assert result['statusCode'] == 200
    watch_job_schedule_queue()

    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
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

    validate_backened(backend, mocked_10_sample_job)
    assert get_job_state(mocked_10_sample_job['id']) == SCHEDULED

    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
    assert len(job) == 10

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

    validate_backened(backend, mocked_10_sample_job)
    # the overal job state is currently processing
    assert get_job_state(mocked_10_sample_job['id']) == PROCESSING

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) in ["scheduled", "processing"]
        assert v in ['scheduled', 'processing']

        # force stasis that all samples have been finished
        response = create.create({'body': json.dumps({'sample': k, 'status': 'exported'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    validate_backened(backend, mocked_10_sample_job)
    # all job items should be in state finished on the stasis side and processed on the job side
    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
    for k, v in job.items():
        assert get_tracked_state(k) == "exported"

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue

    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_queue({}, {})

    validate_backened(backend, mocked_10_sample_job)
    # we should now have jobs in the state aggregation scheduled
    # this means the jobs should be in the aggregator queue
    # but not processed by fargate yet

    validate_backened(backend, mocked_10_sample_job)

    state = get_job_state(mocked_10_sample_job['id'])
    assert state in [AGGREGATING, AGGREGATING_SCHEDULED]  # kinda buggy
    # simulate the receiving of an aggregation event


def test_schedule_job_override_tracking_data(requireMocking, mocked_10_sample_job, backend):
    """
    tests the scheduling of a job
    """

    ##
    # check for the correct backend
    ##
    validate_backened(backend, mocked_10_sample_job)

    # here we do the actual schedulign now
    result = schedule_job({'pathParameters': {
        "job": mocked_10_sample_job['id']
    }}, {})

    watch_job_schedule_queue()
    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
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

    validate_backened(backend, mocked_10_sample_job)
    assert get_job_state(mocked_10_sample_job['id']) == SCHEDULED

    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
    assert len(job) == 10

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

    validate_backened(backend, mocked_10_sample_job)
    # the overal job state is currently processing
    assert get_job_state(mocked_10_sample_job['id']) == PROCESSING

    # all job items should be in state processing
    for k, v in job.items():
        assert get_tracked_state(k) in ["scheduled", "processing"]
        assert v in ['scheduled', 'processing']

        # force stasis that all samples have been finished
        response = create.create({'body': json.dumps({'sample': k, 'status': 'exported'})}, {})

    # sync all normally cron would do this for us
    monitor_jobs({}, {})

    validate_backened(backend, mocked_10_sample_job)
    # all job items should be in state finished on the stasis side and processed on the job side
    job = load_job_samples_with_states(job=mocked_10_sample_job['id'])
    for k, v in job.items():
        assert get_tracked_state(k) == "exported"

    # since AWS only allows to process 10 messages at a time and we have more than that
    # this has to be called several times
    # in production this is driven by a timer
    # and so a none issue

    for x in range(0, math.ceil(len(job) / MESSAGE_BUFFER)):
        monitor_queue({}, {})

    validate_backened(backend, mocked_10_sample_job)
    # we should now have jobs in the state aggregation scheduled
    # this means the jobs should be in the aggregator queue
    # but not processed by fargate yet

    validate_backened(backend, mocked_10_sample_job)

    state = get_job_state(mocked_10_sample_job['id'])
    assert state in [AGGREGATING, AGGREGATING_SCHEDULED]  # kinda buggy

    # simulate the receiving of an aggregation event


def validate_backened(backend, mocked_10_sample_job):
    job_config = get_job_config(mocked_10_sample_job['id'])
    assert job_config['resource'] == backend


@pytest.mark.parametrize("samples", [15, 33, 50, 66, 100, 500])
def test_schedule_job_many_samples(requireMocking, samples):
    """
    tests scheduling very large jobs
    :param requireMocking:
    :return:
    """

    job = {
        "id": "stored_test_job",
        "method": "test",
        "profile": "lcms",
    }

    result = store_job({'body': json.dumps(job)}, {})

    for x in range(1, samples):
        store_sample_for_job({'body': json.dumps({
            "job": job['id'],
            "sample": f"sample_{x}"}
        )}, {})

    assert result['statusCode'] == 200

    result = schedule_job({'pathParameters': {
        "job": job['id']
    }}, {})
    assert result['statusCode'] == 200

    watch_job_schedule_queue()


def watch_job_schedule_queue():
    """
    little helper method, to watch a queue for us during testing
    """
    import boto3
    # receive message from queue
    client = boto3.client('sqs')
    # if topic exists, we just reuse it
    arn = _get_queue(client=client, queue_name="jobQueue", resource=Backend.NO_BACKEND_REQUIRED)
    more_messages = True
    while more_messages:
        message = client.receive_message(
            QueueUrl=arn,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=1,
            VisibilityTimeout=1,
            WaitTimeSeconds=1
        )

        if 'Messages' in message:
            for m in message['Messages']:
                client.delete_message(
                    QueueUrl=arn,
                    ReceiptHandle=m['ReceiptHandle']
                )
                schedule_job_from_queue({'Records': [
                    {
                        'body': m['Body']
                    }
                ]}, {})

        else:
            more_messages = False

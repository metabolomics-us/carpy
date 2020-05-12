import json
import random

from stasis.jobs import tracking
from stasis.jobs.schedule import monitor_jobs
from stasis.jobs.sync import calculate_job_state
from stasis.service.Status import SCHEDULED, AGGREGATING, EXPORTED, FAILED, AGGREGATED, PROCESSING
from stasis.tables import set_job_state
from stasis.tracking import create


def test_create_and_get(requireMocking):
    # upload data
    data = json.dumps({
        "job": "12345",
        "sample": "abc",
        "state": "scheduled"
    })

    result = tracking.create({'body': data}, {})
    # ensure status is correct

    assert result is not None
    assert result['statusCode'] == 200

    result = tracking.get({
        "pathParameters": {
            "sample": "abc",
            "job": "12345"
        }
    }, {})

    assert result is not None

    assert result['statusCode'] == 200
    assert 'body' in result
    result = json.loads(result['body'])
    # upload new data

    # ensure status is updated now

    assert 'job' in result
    assert 'sample' in result
    assert 'state' in result
    assert 'id' in result

    assert result['id'] == '12345_abc'
    assert result['state'] == 'scheduled'

    # check if update works correctly
    data = json.dumps({
        "job": "12345",
        "sample": "abc",
        "state": "processing"
    })

    result = tracking.create({'body': data}, {})
    calculate_job_state("12345")
    result = tracking.get({
        "pathParameters": {
            "sample": "abc",
            "job": "12345"
        }
    }, {})

    assert result is not None

    assert result['statusCode'] == 200
    assert 'body' in result
    result = json.loads(result['body'])

    assert result['state'] == 'processing'
    print(result)
    assert 'past_states' in result
    assert 'scheduled' in result['past_states']


def test_status_not_found(requireMocking):
    result = tracking.status({
        "pathParameters": {
            "job": "123456789"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 404


def test_status(requireMocking):
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "123456",
            "sample": "abc_{}".format(x),
            "state": "scheduled"
        })

        # store in stasis or we doomed!!!
        response = create.create({'body': json.dumps({'sample': 'abc_{}'.format(x), 'status': 'scheduled'})}, {})

        # store in the job state table
        result = tracking.create({'body': data}, {})

        assert result['statusCode'] == 200

    set_job_state(job="123456", method="test", profile="test",
                  state=SCHEDULED)

    result = tracking.status({
        "pathParameters": {
            "job": "123456",
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['job_state'] == 'scheduled'

    for x in range(0, 10):
        # pretend stasis has now exported the data
        response = create.create({'body': json.dumps({'sample': 'abc_{}'.format(x), 'status': 'exported'})}, {})

    calculate_job_state("123456")
    result = tracking.status({
        "pathParameters": {
            "job": "123456",
        }
    }, {})

    # since not yet aggregated, the job should be in state processing
    assert json.loads(result['body'])['job_state'] == 'processing'

    for x in range(0, 100):
        # pretend all samples are finished
        response = create.create({'body': json.dumps({'sample': 'abc_{}'.format(x), 'status': "finished"})}, {})

    result = tracking.status({
        "pathParameters": {
            "job": "123456",
        }
    }, {})

    monitor_jobs({}, {})

    assert json.loads(result['body'])['job_state'] == PROCESSING


def test_description(requireMocking):
    for x in range(0, 40):
        # upload data
        data = json.dumps({
            "job": "1234567",
            "sample": "abc_{}".format(x),
            "state": "scheduled"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.description({
        "pathParameters": {
            "job": "1234567",
            "psize": 25,
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    samples = json.loads(result['body'])

    assert len(samples) == 25

    result = tracking.description({
        "pathParameters": {
            "job": "1234567",
            "psize": 25,
            "last_key": samples[-1]['id']
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200
    assert len(json.loads(result['body'])) == 15

import json
import random

from jobs import tracking
from jobs.tracking import States


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
        "state": "processed"
    })

    result = tracking.create({'body': data}, {})

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

    assert result['state'] == 'processed'
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

        result = tracking.create({'body': data}, {})

    result = tracking.status({
        "pathParameters": {
            "job": "123456"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert len(json.loads(result['body'])['states']) == 1

    assert json.loads(result['body'])['dstate'] == 'scheduled'
    for x in range(0, 10):
        # upload data
        data = json.dumps({
            "job": "123456",
            "sample": "abc_{}".format(x),
            "state": "processed"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.status({
        "pathParameters": {
            "job": "123456"
        }
    }, {})

    assert len(json.loads(result['body'])['states']) == 2
    assert json.loads(result['body'])['dstate'] == 'scheduled'

    for x in range(20, 70):
        # upload data
        data = json.dumps({
            "job": "123456",
            "sample": "abc_{}".format(x),
            "state": "done"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.status({
        "pathParameters": {
            "job": "123456"
        }
    }, {})

    assert len(json.loads(result['body'])['states']) == 3
    assert json.loads(result['body'])['dstate'] == 'done'


def test_description(requireMocking):
    for x in range(0, 1000):
        # upload data
        data = json.dumps({
            "job": "1234567",
            "sample": "abc_{}".format(x),
            "state": "scheduled"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.description({
        "pathParameters": {
            "job": "1234567"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert len(json.loads(result['body'])) == 1000


def test_job_can_aggregate_is_false(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-aggregate",
            "sample": "abc_{}".format(x),
            "state": "scheduled"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_can_aggregate({
        "pathParameters": {
            "job": "1234567-aggregate"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['can_aggregate'] is False


def test_job_can_aggregate_is_true_for_failed(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-aggregate",
            "sample": "abc_{}".format(x),
            "state": "failed"
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_can_aggregate({
        "pathParameters": {
            "job": "1234567-aggregate"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['can_aggregate'] is True


def test_job_can_aggregate_is_true_for_processed(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-aggregate",
            "sample": "abc_{}".format(x),
            "state": str(States.PROCESSED)
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_can_aggregate({
        "pathParameters": {
            "job": "1234567-aggregate"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['can_aggregate'] is True


def test_job_can_aggregate_is_true_for_processed_and_failed(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-aggregate",
            "sample": "abc_{}".format(x),
            "state": random.choice([str(States.PROCESSED), str(States.FAILED)])
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_can_aggregate({
        "pathParameters": {
            "job": "1234567-aggregate"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['can_aggregate'] is True


def test_job_is_done_is_false(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-done",
            "sample": "abc_{}".format(x),
            "state": random.choice([str(States.SCHEDULED), str(States.AGGREGATING), str(States.PROCESSED)])
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_is_done({
        "pathParameters": {
            "job": "1234567-done"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['is_done'] is False


def test_job_is_done_is_true_for_processed_and_failed(requireMocking):
    # schedule job
    for x in range(0, 100):
        # upload data
        data = json.dumps({
            "job": "1234567-done",
            "sample": "abc_{}".format(x),
            "state": random.choice([str(States.AGGREGATED), str(States.FAILED)])
        })

        result = tracking.create({'body': data}, {})

    result = tracking.job_is_done({
        "pathParameters": {
            "job": "1234567-done"
        }
    }, {})

    assert result is not None
    assert result['statusCode'] == 200

    assert json.loads(result['body'])['is_done'] is True

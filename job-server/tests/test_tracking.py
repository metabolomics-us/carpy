import json

from jobs import tracking


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

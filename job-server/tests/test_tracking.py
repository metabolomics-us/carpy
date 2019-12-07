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

    assert False

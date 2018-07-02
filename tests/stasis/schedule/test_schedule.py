import time

import simplejson as json

from stasis.schedule import schedule as s
from stasis.tracking import get


def test_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'env': 'test', 'method': 'hello', 'mode': 'lcms', 'task_version': '1'})

    response = s.schedule({'body': jsonString}, {})

    assert response['statusCode'] == 200

    # ensure we have a new tracking object
    result = json.loads(get.get({
        "pathParameters": {
            "sample": "myTest"
        }
    }, {})['body'])
    assert result['status'][0]['value'] == "scheduled"


def test_schedule_failed(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {'sample': 'myTest', 'env': 'test', 'method': 'hello', 'mode': 'lcms', 'task_version': '111'})

    response = s.schedule({'body': jsonString}, {})

    assert response['statusCode'] == 503

    # ensure we have a new tracking object
    result = json.loads(get.get({
        "pathParameters": {
            "sample": "myTest"
        }
    }, {})['body'])

    assert result['status'][0]['value'] == "failed"

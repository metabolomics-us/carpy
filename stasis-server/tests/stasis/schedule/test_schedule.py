import time

import simplejson as json

from stasis.schedule import schedule as s


def test_scheduled_task_size(requireMocking):
    s.scheduled_task_size({}, {})


def test_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms', 'task_version': '86'})

    response = s.schedule({'body': jsonString}, {})

    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']

    s.monitor_queue({}, {})


def test_secure_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {'secured': True, 'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms'})

    response = s.secure_schedule({'body': jsonString}, {})

    assert 'isBase64Encoded'in response
    assert 200 == response['statusCode']
    assert 'secured' in response['body']
    assert json.loads(response['body'])['secured'] == True

    s.monitor_queue({}, {})

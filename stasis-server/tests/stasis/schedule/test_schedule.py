import time

import simplejson as json
from pytest import fail

from stasis.schedule import schedule as s
from stasis.tracking import get


def test_scheduled_task_size(requireMocking):
    response = s.scheduled_task_size({}, {})


def test_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms', 'task_version': '1'})

    response = s.schedule({'body': jsonString}, {})

    assert 200 == response['statusCode']

    s.monitor_queue({}, {})

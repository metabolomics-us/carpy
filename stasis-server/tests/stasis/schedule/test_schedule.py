import time

import simplejson as json

from stasis.schedule import schedule as s
from stasis.schedule.schedule import SECURE_CARROT_RUNNER, MAX_FARGATE_TASKS, MAX_FARGATE_TASKS_BY_SERVICE


def test_current_tasks(requireMocking):
    jsonString = json.dumps(
        {'secured': True, 'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms', 'task_version': 1})

    response = s.schedule({'body': jsonString}, {})
    response = s.schedule({'body': jsonString}, {})
    response = s.schedule({'body': jsonString}, {})
    response = s.schedule({'body': jsonString}, {})
    response = s.schedule({'body': jsonString}, {})

    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    assert 'secured' in response['body']
    assert json.loads(response['body'])['secured'] == True

    s.monitor_queue({}, {})
    print(s.current_tasks({}, {}))

    assert len(json.loads(s.current_tasks({}, {})['body'])['tasks']) == 5


def test_scheduled_task_size(requireMocking):
    s.scheduled_task_size({}, {})


def test_schedule(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps(
        {'secured': True, 'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms', 'task_version': 1})

    response = s.schedule({'body': jsonString}, {})

    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    assert 'secured' in response['body']
    assert json.loads(response['body'])['secured'] == True

    s.monitor_queue({}, {})


def test__free_task_count_no_service(requireMocking):
    jsonString = json.dumps(
        {'secured': True, 'sample': 'myTest', 'env': 'test', 'method': 'hello', 'profile': 'lcms', 'task_version': 1})

    for x in range(0, MAX_FARGATE_TASKS_BY_SERVICE[SECURE_CARROT_RUNNER]):
        response = s.schedule({'body': jsonString}, {})
        s.monitor_queue({}, {})

        tasks_for_service = s._free_task_count(service=SECURE_CARROT_RUNNER)
        max_tasks_for_service = MAX_FARGATE_TASKS_BY_SERVICE[SECURE_CARROT_RUNNER]

        assert max_tasks_for_service - x - 1 == tasks_for_service

    assert s._free_task_count(service=SECURE_CARROT_RUNNER) == 0
    assert s._free_task_count() == MAX_FARGATE_TASKS - MAX_FARGATE_TASKS_BY_SERVICE[
        SECURE_CARROT_RUNNER]

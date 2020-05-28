import os
import traceback
from typing import Optional

import simplejson as json
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.config import SECURE_CARROT_RUNNER, SECURE_CARROT_AGGREGATOR, MAX_FARGATE_TASKS_BY_SERVICE, \
    MAX_FARGATE_TASKS
from stasis.schema import __SCHEDULE__
from stasis.service.Status import FAILED
from stasis.tables import update_job_state
from stasis.tracking.create import create


def send_to_fargate(overrides, task_name):
    """
    sends the computation to the actual fargate cluster
    :param overrides:
    :param task_name:
    :return:
    """
    # fire AWS fargate instance now
    import boto3
    client = boto3.client('ecs')
    response = client.run_task(
        cluster='carrot',  # name of the cluster
        launchType='FARGATE',
        taskDefinition=task_name,
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    # we need at least 2, to insure network stability
                    # these have been manually created and need to be shared with the db server
                    'subnet-e382339a',
                    'subnet-04c0515e',
                    'subnet-b779a9fc',
                    'subnet-39f3df11'
                ],
                'assignPublicIp': 'ENABLED'
            }
        },
        overrides=overrides,
    )
    return response


def schedule_processing_to_fargate(event, context):
    """
    submits a new task to the cluster - a fargate task will run it
    :param event:
    :param context:
    :return:
    """
    body = json.loads(event['body'])

    try:

        validate(body, __SCHEDULE__)
        import boto3
        overrides = {"containerOverrides": [{
            "name": "carrot-runner",
            "environment": [
                {
                    "name": "SPRING_PROFILES_ACTIVE",
                    "value": "{}{},{}".format('aws', os.getenv('current_stage'), body["profile"])
                    # AWS profile needs to be active for this system to connect to the AWS database
                },
                {
                    "name": "CARROT_SAMPLE",
                    "value": "{}".format(body['sample'])
                },
                {
                    "name": "CARROT_METHOD",
                    "value": "{}".format(body['method'])
                },
                {
                    "name": "CARROT_MODE",
                    "value": "{}".format(body['profile'])
                },

            ]
        }]}

        task_name = "{}-{}".format(os.getenv("current_stage"), SECURE_CARROT_RUNNER)

        if 'key' in body and body['key'] is not None:
            overrides['containerOverrides'][0]['environment'].append({
                "name": "STASIS_KEY",
                "value": body['key']
            })

        send_to_fargate(overrides=overrides, task_name=task_name)

        create({"body": json.dumps({'sample': body['sample'], 'status': 'scheduled'})}, {})

        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }

    except ValidationError as e:
        print("validation error")
        print(body)
        traceback.print_exc()

        return {
            'body': json.dumps(str(e)),
            'statusCode': 503,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }
        pass
    except Exception as e:
        print(body)
        traceback.print_exc()
        create({"body": json.dumps({'sample': body['sample'], 'status': FAILED, 'reason': str(e)})}, {})

        return {
            'body': json.dumps(str(e)),
            'statusCode': 503,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }


def schedule_aggregation_to_fargate(param, param1):
    assert 'body' in param, "please ensure you have a body set!"
    assert 'job' in param['body'], "please ensure your body contains the job name"

    body = param['body']

    try:
        job = json.loads(param['body'])['job']

        import boto3
        overrides = {"containerOverrides": [{
            "name": "carrot-aggregator",
            "environment": [
                {
                    "name": "CARROT_JOB",
                    "value": "{}".format(job)
                }
            ]
        }]}

        task_name = "{}-{}".format(os.getenv("current_stage"), SECURE_CARROT_AGGREGATOR)

        if 'key' in body and body['key'] is not None:
            overrides['containerOverrides'][0]['environment'].append({
                "name": "STASIS_API_TOKEN",
                "value": body['key']
            })

        if 'url' in body and body['url'] is not None:
            overrides['containerOverrides'][0]['environment'].append({
                "name": "STASIS_URL",
                "value": body['url']
            })

        print('utilizing taskDefinition: {}'.format(task_name))
        print(overrides)
        print("")

        response = send_to_fargate(overrides, task_name)

        print(f'Response: {response}')
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }
    except Exception as e:
        update_job_state(job=body['job'], state=FAILED, reason="job failed to aggregate due to %".format(str(e)))
        raise e


def _current_tasks():
    """
    a list of all current tasks in the system
    :return:
    """
    import boto3
    client = boto3.client('ecs')
    result = client.list_tasks(cluster='carrot')['taskArns']

    if len(result) > 0:
        desc = client.describe_tasks(cluster="carrot", tasks=result)
        tasks = []
        if 'tasks' in desc:
            for task in desc['tasks']:
                name = task['taskDefinitionArn'].split(':')[-2].split("/")[-1]

                tasks.append({
                    "name": name.replace("{}-".format(os.getenv("current_stage")), ''),
                    "state": task['lastStatus']
                })

        return tasks
    else:
        return []


def _free_task_count(service: Optional[str] = None) -> int:
    """
    reports the free task count by either
    :param service:
    :return:
    """
    tasks = _current_tasks()

    if service is None:

        result = len(tasks)

        if result > (MAX_FARGATE_TASKS - 1):
            print("fargate queue was full, no scheduling possible")
            return 0
        else:
            return MAX_FARGATE_TASKS - result
    else:
        filtered_tasks = list(filter(lambda d: d['name'] == service, tasks))
        result = len(filtered_tasks)
        if result > (MAX_FARGATE_TASKS_BY_SERVICE[service] - 1):
            print("fargate queue was full for service {}, no scheduling possible".format(service))
            return 0
        else:
            return MAX_FARGATE_TASKS_BY_SERVICE[service] - result
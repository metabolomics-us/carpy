import os
import traceback
from typing import Optional

import simplejson as json
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.jobs.states import States
from stasis.schema import __SCHEDULE__
from stasis.tables import update_job_state
from stasis.tracking.create import create

SERVICE = "stasis-service"
MESSAGE_BUFFER = 10
SECURE_CARROT_RUNNER = 'secure-carrot-runner'
SECURE_CARROT_AGGREGATOR = 'secure-carrot-aggregator'

MAX_FARGATE_TASKS_BY_SERVICE = {
    SECURE_CARROT_RUNNER: 40,
    SECURE_CARROT_AGGREGATOR: 10

}

MAX_FARGATE_TASKS = sum(MAX_FARGATE_TASKS_BY_SERVICE.values())


def current_tasks(event, context):
    """
    returns all the currently running tasks
    :param event:
    :param context:
    :return:
    """

    tasks = _current_tasks()

    return {
        'body': json.dumps({'tasks': tasks}),
        'statusCode': 200,
        'headers': __HTTP_HEADERS__
    }


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
                    "name": name,
                    "state": task['lastStatus']
                })
        return tasks
    else:
        return []


def scheduled_task_size(event, context):
    """

    returns the current count of tasks in the fargate cluster list. This is required to ensure we are not overwhelming the cluster
    by scheduling more tasks than we are allowed to run at any given time
    :param event:
    :param context:
    :return:
    """
    total_count = len(_current_tasks())

    return {
        'body': json.dumps({'count': total_count}),
        'statusCode': 200,
        'headers': __HTTP_HEADERS__
    }


def schedule(event, context):
    """
    schedules the given even to the internal queuing system
    :param event:
    :param context:
    :return:
    """
    body = json.loads(event['body'])
    return schedule_to_queue(body, service=SECURE_CARROT_RUNNER)


def schedule_to_queue(body, service: str):
    body['secured'] = True
    body[SERVICE] = service

    # get topic refrence
    import boto3
    client = boto3.client('sqs')
    # if topic exists, we just reuse it
    arn = _get_queue(client)
    serialized = json.dumps(body, use_decimal=True)
    # submit item to queue for routing to the correct persistence
    result = client.send_message(
        QueueUrl=arn,
        MessageBody=json.dumps({'default': serialized}),
    )

    return {
        'statusCode': result['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__,
        'isBase64Encoded': False,
        'body': serialized
    }


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

        version = '1'
        task_name = SECURE_CARROT_AGGREGATOR
        if 'task_version' in body:
            version = body["task_version"]

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

        print('utilizing taskDefinition: {}:{}'.format(task_name, version))
        print(overrides)
        print("")

        # fire AWS fargate instance now
        client = boto3.client('ecs')
        response = client.run_task(
            cluster='carrot',  # name of the cluster
            launchType='FARGATE',
            taskDefinition='{}:{}'.format(task_name, version),
            count=1,
            platformVersion='LATEST',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        # we need at least 2, to insure network stability
                        os.environ.get('SUBNET', 'subnet-064fbf05a666c6557')],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides=overrides,
        )

        update_job_state(job=job, state=States.AGGREGATION_SCHEDULED)
        print(f'Response: {response}')
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }
    except Exception as e:
        raise e


def monitor_queue(event, context):
    """
    monitors the fargate queue and if task size is less than < x it will
    try to schedule new tasks. This should be called from cron or another
    scheduled interval
    :param event:
    :param context:
    :return:
    """

    import boto3
    # receive message from queue
    client = boto3.client('sqs')

    # if topic exists, we just reuse it
    arn = _get_queue(client)

    slots = _free_task_count()

    if slots == 0:
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }

    print("we have: {} slots free for tasks".format(slots))

    message_count = slots if 0 < slots <= MESSAGE_BUFFER else MESSAGE_BUFFER if slots > 0 else 1
    message = client.receive_message(
        QueueUrl=arn,
        AttributeNames=[
            'All'
        ],
        # MessageAttributeNames=[
        #     'string',
        # ],
        MaxNumberOfMessages=message_count,
        VisibilityTimeout=1,
        WaitTimeSeconds=1
        # ReceiveRequestAttemptId='string'
    )

    if 'Messages' not in message:
        print("no messages received: {}".format(message))
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }

    messages = message['Messages']

    if len(messages) > 0:
        # print("received {} messages".format(len(messages)))
        result = []
        # print(messages)
        for message in messages:
            receipt_handle = message['ReceiptHandle']
            # print("current message: {}".format(message))
            body = json.loads(json.loads(message['Body'])['default'])
            # print("schedule: {}".format(body))
            try:

                slots = _free_task_count(service=body[SERVICE])

                print(body)

                if slots > 0:
                    if body[SERVICE] == SECURE_CARROT_RUNNER:
                        result.append(schedule_processing_to_fargate({'body': json.dumps(body)}, {}))
                    elif body[SERVICE] == SECURE_CARROT_AGGREGATOR:
                        result.append(schedule_aggregation_to_fargate({'body': json.dumps(body)}, {}))
                    else:
                        raise Exception("unknown service specified: {}".format(body[SERVICE]))

                    client.delete_message(
                        QueueUrl=arn,
                        ReceiptHandle=receipt_handle
                    )
                else:
                    # nothing found
                    pass
            except Exception as e:
                traceback.print_exc()
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
            'body': json.dumps({'scheduled': len(result)})
        }

    else:
        print("no messages received!")
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }


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
                    "value": "{},{}".format(body['env'], body['profile'])
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
                }
            ]
        }]}

        version = '1'
        task_name = SECURE_CARROT_RUNNER
        if 'task_version' in body:
            version = body["task_version"]

        if 'key' in body and body['key'] is not None:
            overrides['containerOverrides'][0]['environment'].append({
                "name": "STASIS_KEY",
                "value": body['key']
            })

        print('utilizing taskDefinition: {}:{}'.format(task_name, version))
        print(overrides)
        print("")

        # fire AWS fargate instance now
        client = boto3.client('ecs')
        response = client.run_task(
            cluster='carrot',  # name of the cluster
            launchType='FARGATE',
            taskDefinition='{}:{}'.format(task_name, version),
            count=1,
            platformVersion='LATEST',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        # we need at least 2, to insure network stability
                        os.environ.get('SUBNET', 'subnet-064fbf05a666c6557')],
                    'assignPublicIp': 'ENABLED'
                }
            },
            overrides=overrides,
        )

        create({"body": json.dumps({'sample': body['sample'], 'status': 'scheduled'})}, {})

        # fire status update to track sample is in scheduling

        print(f'Response: {response}')
        return {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }

    except Exception as e:

        traceback.print_exc()
        create({"body": json.dumps({'sample': body['sample'], 'status': 'failed'})}, {})

        return {
            'body': json.dumps(str(e)),
            'statusCode': 503,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }


def _get_queue(client, queue_name: str = "schedule_queue"):
    """
    generates queues for us on demand as required
    """
    try:
        print("new queue")
        return client.create_queue(QueueName=os.environ[queue_name])['QueueUrl']
    except Exception as ex:
        print("queue exists")
        return client.get_queue_url(QueueName=os.environ[queue_name])['QueueUrl']

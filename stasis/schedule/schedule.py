import os

import traceback
import simplejson as json
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __SCHEDULE__
from stasis.service.Queue import Queue
from stasis.tracking.create import create

MAX_FARGATE_TASKS = 50


def scheduled_queue_size(event, context):
    """
    returns the size of the current queue, utilized for scheduling
    :param event:
    :param context:
    :return:
    """


def scheduled_task_size(event, context):
    """

    returns the current count of tasks in the fargate cluster list. This is required to ensure we are not overwhelming the cluster
    by scheduling more tasks than we are allowed to run at any given time
    :param event:
    :param context:
    :return:
    """

    import boto3
    client = boto3.client('ecs')

    result = len(client.list_tasks(cluster='carrot')['taskArns'])

    print(result)
    return {
        'body': json.dumps({'count': result}),
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

    # get topic refrence
    import boto3
    client = boto3.client('sqs')

    # if topic exists, we just reuse it
    arn = client.create_queue(QueueName=os.environ['schedule_queue'])['QueueUrl']

    serialized = json.dumps(body, use_decimal=True)
    # submit item to queue for routing to the correct persistence

    result = client.send_message(
        QueueUrl=arn,
        MessageBody=json.dumps({'default': serialized}),
    )

    print(result)
    return {
        'statusCode': result['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__,
        'body': serialized
    }


def _free_task_count() -> int:
    # 1. check fargate queue

    import boto3
    client = boto3.client('ecs')

    result = len(client.list_tasks(cluster='carrot')['taskArns'])

    if result > (MAX_FARGATE_TASKS - 1):
        print("fargate queue was full, no scheduling possible")
        return 0
    else:
        return MAX_FARGATE_TASKS - result


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
    arn = client.create_queue(QueueName=os.environ['schedule_queue'])['QueueUrl']

    slots = _free_task_count()

    if slots == 0:
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }

    print("we have: {} slots free for tasks".format(slots))

    message = client.receive_message(
        QueueUrl=arn,
        AttributeNames=[
            'All'
        ],
        MessageAttributeNames=[
            'string',
        ],
        MaxNumberOfMessages=_free_task_count(),
        VisibilityTimeout=1,
        WaitTimeSeconds=1,
        ReceiveRequestAttemptId='string'
    )

    if 'Messages' not in message:
        print("no messages received: {}".format(message))
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }

    messages = message['Messages']

    if len(messages) > 0:
        print("received {} messages".format(len(messages)))
        result = []
        print(messages)
        for message in messages:
            print("current message: {}".format(message))
            body = json.loads(message['Body'])['default']
            print("schedule: {}".format(body))
            result.append(schedule_to_fargate({'body': body}, {}))

        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'scheduled': len(result)})
        }

    else:
        print("no messages received!")
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }


def schedule_to_fargate(event, context):
    """
    triggers a new calculation task on the fargate server
    :param event:
    :param context:
    :return:
    """
    """
        submits a new task to the cluster - a fargate task will run it

    :param configuration:
    :param user:
    :return:
    """
    body = json.loads(event['body'])

    print(body)
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

        version = "1"

        if "task_version" in body:
            version = body["task_version"]

        print("utilizing version: {}".format(version))

        # fire AWS fargate instance now
        client = boto3.client('ecs')
        response = client.run_task(
            cluster='carrot',  # name of the cluster
            launchType='FARGATE',
            taskDefinition='carrot-runner:{}'.format(version),
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

        print(response)
        return {
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }

    except Exception as e:

        traceback.print_exc()
        create({"body": json.dumps({'sample': body['sample'], 'status': 'failed'})}, {})

        return {
            'body': json.dumps(str(e)),
            'statusCode': 503,
            'headers': __HTTP_HEADERS__
        }

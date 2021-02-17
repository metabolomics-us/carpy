import os
from typing import Optional

import simplejson as json
from jsonschema import validate

from stasis.config import SERVICE, SECURE_CARROT_RUNNER
from stasis.headers import __HTTP_HEADERS__
from stasis.schedule.backend import Backend, DEFAULT_PROCESSING_BACKEND
from stasis.schedule.fargate import _current_tasks
from stasis.schema import __SCHEDULE__


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


def schedule_queue(event, context):
    # get topic refrence
    import boto3
    client = boto3.client('sqs')

    queue = _get_queue(client)

    return {
        'body': json.dumps({'queue': queue}),
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

    if 'resource' in body:
        resource = Backend(body['resource'])
    else:
        resource = DEFAULT_PROCESSING_BACKEND

    validate(body, __SCHEDULE__)
    print(f"scheduling {body} to queue")
    return schedule_to_queue(body, service=SECURE_CARROT_RUNNER, resource=resource)


def schedule_to_queue(body, service: Optional[str], resource: Backend, queue_name="schedule_queue"):
    """
    general way to schedule something to a queue
    :param body:
    :param service:
    :param resource:
    :param queue_name:
    :return:
    """
    body['secured'] = True

    print(f"scheduling {body} to queue {queue_name}")
    if service is not None:
        body[SERVICE] = service

    # get topic refrence
    import boto3
    client = boto3.client('sqs')
    # if topic exists, we just reuse it
    arn = _get_queue(client, resource=resource, queue_name=queue_name)
    serialized = json.dumps(body, use_decimal=True)
    # submit item to queue for routing to the correct persistence
    print(f"arn is {arn}")
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


def _get_queue(client, queue_name: str = "schedule_queue", resource: Backend = None):
    """
    generates queues for us on demand as required
    """
    if resource is None:
        resource = DEFAULT_PROCESSING_BACKEND

    if resource is Backend.NO_BACKEND_REQUIRED:
        name = "{}".format(os.environ[queue_name])
    else:
        name = "{}_{}".format(os.environ[queue_name], resource.value)

    try:
        return client.create_queue(QueueName=name)['QueueUrl']
    except KeyError as ex:
        raise Exception(
            "you forgot to specify your env variable {} to define the queue which you want to create/monitor".format(
                queue_name))
    except Exception as ex:
        return client.get_queue_url(QueueName=os.environ[name])['QueueUrl']

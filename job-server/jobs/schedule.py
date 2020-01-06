import json
import os

from jobs.headers import __HTTP_HEADERS__


def schedule(event, context):
    """
    schedules a task to the processing queue as well as the aggregation queue
    """

    # 1. send to statis processing queue
    # 2. send to aggregating queue


def schedule_processing(event, context):
    """
    schedules the actual processing
    """

    body = json.loads(event['body'])

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


def schedule_aggregation(event, context):
    """
    schedules the actual aggregation
    """

    body = json.loads(event['body'])

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


def _get_queue(client, queue_name):
    try:
        print("new queue")
        return client.create_queue(QueueName=queue_name)['QueueUrl']
    except Exception as ex:
        print("queue exists")
        return client.get_queue_url(QueueName=queue_name)['QueueUrl']

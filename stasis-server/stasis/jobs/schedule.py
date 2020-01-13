import json
import os

from stasis.headers import __HTTP_HEADERS__


def schedule_processing(event, context):
    """
    schedules the actual processing of the job. Internally a lambda function will listen to the queue
    and process this task in the backend to increase responsiveness
    """

    body = json.loads(event['body'])

    # get topic reference
    import boto3
    client = boto3.client('sqs')

    # if topic exists, we just reuse it
    arn = _get_queue(client, os.environ["processing_queue"])

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
    arn = _get_queue(client, os.environ["aggregation_queue"])

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
        return client.create_queue(QueueName=queue_name)['QueueUrl']
    except Exception as ex:
        return client.get_queue_url(QueueName=queue_name)['QueueUrl']

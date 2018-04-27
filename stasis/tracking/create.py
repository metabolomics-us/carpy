import json
import logging
import time
import os
import boto3
import json

# valid states for tracking of samples
validStates = ['entered', 'acquired', 'converted', 'processing', 'exported']


def create(event, context):
    """
        creates a new sample tracking object

        :param event:
        :param context:
        :return:
    """

    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")

    data = json.loads(event['body'])
    if 'sample' not in data:
        logging.error("Validation Failed")
        raise Exception("please ensure you provide the 'sample' property in the object")
    if 'status' not in data:
        logging.error("Validation Failed")
        raise Exception("please provide the 'status' property in the object")
    if data['status'].lower() not in validStates:
        raise Exception(
            "please provide the 'status' property in the object, is one of the following: " + '.'.join(validStates))

    # get topic refrence
    client = boto3.client('sns')

    # if topic exists, we just reuse it
    topic_arn = client.create_topic(Name=os.environ['topic'])['TopicArn']

    # if validation passes, persist the object in the dynamo db

    timestamp = int(time.time() * 1000)

    item = {
        'id': data['sample'],
        'sample': data['sample'],
        'status': [
            {
                'time': timestamp,
                'value': data['status'].upper()
            }
        ]
    }

    serialized = json.dumps(item)
    # submit item to queue for routing to the correct persistence

    result = client.publish(
        TopicArn=topic_arn,
        Message=json.dumps({'default': serialized}),
        Subject="route:tracking",
        MessageStructure='json',
        MessageAttributes={
            'route': {
                'DataType': 'String',
                'StringValue': 'tracking'
            }
        },
    )

    print(result)

    # create a response
    response = {
        "statusCode": result['ResponseMetadata']['HTTPStatusCode'],
        "body": serialized

    }

    return response

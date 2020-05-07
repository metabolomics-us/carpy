import traceback

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.schedule.schedule import _get_queue, _free_task_count, SECURE_CARROT_RUNNER, SECURE_CARROT_AGGREGATOR, \
    MESSAGE_BUFFER, SERVICE, schedule_processing_to_fargate, schedule_aggregation_to_fargate


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
    arn = _get_queue(client=client)

    slots = _free_task_count(service=SECURE_CARROT_RUNNER) + _free_task_count(service=SECURE_CARROT_AGGREGATOR)

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
        MaxNumberOfMessages=message_count,
        VisibilityTimeout=1,
        WaitTimeSeconds=1
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
            body = json.loads(json.loads(message['Body'])['default'])
            try:

                slots = _free_task_count(service=body[SERVICE])

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
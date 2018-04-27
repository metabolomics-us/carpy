from stasis.service import Queue
import logging
import time
import json

# valid states for tracking of samples
validStates = ['entered', 'acquired', 'converted', 'processing', 'exported']


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """

    if 'sample' not in data:
        logging.error("Validation Failed")
        raise Exception("please ensure you provide the 'sample' property in the object")
    if 'status' not in data:
        logging.error("Validation Failed")
        raise Exception("please provide the 'status' property in the object")
    if data['status'].lower() not in validStates:
        raise Exception(
            "please provide the 'status' property in the object, is one of the following: " + '.'.join(validStates))

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

    x = Queue.Queue()
    return x.submit(item, "tracking")


def create(event, context):
    """
        creates a new sample tracking object, from a html api request

        :param event:
        :param context:
        :return:
    """

    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")

    data = json.loads(event['body'])

    return triggerEvent(data)

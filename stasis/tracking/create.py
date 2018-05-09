import simplejson as json
import time

from stasis.service.Queue import Queue
from jsonschema import validate
from stasis.service.Status import Status

dataSchema = {
    'sample': {
        'type': 'string'
    },
    'status': {
        'type': 'string'
    },
    'required': ['sample', 'status']
}


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """

    validate(data, dataSchema)

    statusService = Status()
    if not statusService.valid(data['status']):
        raise Exception(
            "please provide the 'status' property in the object")

    # if validation passes, persist the object in the dynamo db

    timestamp = int(time.time() * 1000)

    item = {
        'id': data['sample'],
        'sample': data['sample'],
        'status': [
            {
                'time': timestamp,
                'value': data['status'].lower(),
                'priority': statusService.priority(data['status'])
            }
        ]
    }

    x = Queue()
    return x.submit(item, "tracking")


def create(event, context):
    """
        creates a new sample tracking object, from a html api request

        :param event:
        :param context:
        :return:
    """

    if 'body' not in event:
        "http://minix.fiehnlab.ucdavis.edu/rest/export/"
    data = json.loads(event['body'])

    return triggerEvent(data)

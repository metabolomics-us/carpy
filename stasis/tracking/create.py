import simplejson as json
import time

from stasis.service.Queue import Queue
from jsonschema import validate
from stasis.service.Status import Status
from stasis.schema import __TRACKING_SCHEMA__


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample and status in it, to be considered validd
    :return: a serialized version of the submitted message
    """

    validate(data, __TRACKING_SCHEMA__)

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

    if "fileHandle" in data:
        item['status']['fileHandle'] = data['fileHandle']

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
        raise Exception("please ensure you provide a valid body")
    data = json.loads(event['body'])

    return triggerEvent(data)

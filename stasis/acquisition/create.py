from stasis.service.Queue import Queue
import time
import simplejson as json
from jsonschema import validate
from stasis.schema import __ACQUISITION_SCHEMA__

def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample
    :return: a serialized version of the submitted message
    """

    print("trigger event: " + json.dumps(data, indent=2))

    validate(data, __ACQUISITION_SCHEMA__)

    timestamp = int(time.time() * 1000)
    data['time'] = timestamp
    data['id'] = data['sample']

    x = Queue()
    return x.submit(data, "metadata")


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


def fromMinix(event, context):
    """
        submits all the samples from the given minix study to the system for usage
    :param event:
    :param context:
    :return:
    """

    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")

    data = json.loads(event['body'])

    url = "http://minix.fiehnlab.ucdavis.edu/rest/export/"
    if 'url' in data:
        url = data['url']

    if 'id' not in data:
        raise Exception("please ensure you provide a an id!")

    url += str(data['id'])

    data['url'] = url
    data['minix'] = True

    x = Queue()
    return x.submit(data, "metadata")

from stasis.service.Queue import Queue
import time
import simplejson as json
from jsonschema import validate

# defines the schema of the incoming data object
dataSchema = {
    'sample': {
        'type': 'string'
    },
    'acquisition': {
        'instrument': {
            'type': 'string'
        },
        'name': {
            'type': 'string'
        },
        'ionisation': {
            'type': 'string'
        },
        'method': {
            'type': 'string'
        },

        'required': ['instrument', 'name', 'ionisation', 'method']
    },
    'metadata': {
        'class': {
            'type': 'string'
        },
        'species': {
            'type': 'string'
        },
        'organ': {
            'type': 'string'
        },

        'required': ['class', 'species', 'organ']
    },
    'userdata': {
        'label': {
            'type': 'string'
        },
        'comment': {
            'type': 'string'
        },

        'required': ['label', 'comment']
    },

    'required': ['userdata', 'metadata', 'acquisition', 'sample']
}


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample
    :return: a serialized version of the submitted message
    """

    print("trigger event: " + json.dumps(data, indent=2))

    timestamp = int(time.time() * 1000)
    data['time'] = timestamp
    data['id'] = data['sample']

    validate(data, dataSchema)

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

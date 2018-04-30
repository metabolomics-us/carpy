from stasis.service.Queue import Queue
import logging
import time
import json
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

    timestamp = int(time.time() * 1000)
    data['time'] = timestamp

    validate(data, dataSchema)
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

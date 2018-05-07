from stasis.service.Queue import Queue
import time
import json
from jsonschema import validate

# defines the schema of the incoming data object
dataSchema = {
    'sample': {
        'type': 'string'
    },
    'time': {
        'type': 'long'
    }
    ,
    'results': {
        'type': 'array',
        'items': {

            'type': 'object',
            'properties': {

                'target': {
                    'retentionIndex': {
                        'type': 'double'
                    },
                    'name': {
                        'type': 'string'
                    },
                    'id': {
                        'type': 'string'
                    },
                    'mass': {
                        'type': 'double'
                    }
                },

                'annotation': {
                    'retentionIndex': {
                        'type': 'double'
                    },
                    'mass': {
                        'type': 'double'
                    },
                    'intensity': {
                        'type': 'double'
                    },
                    'replaced': {
                        'type': 'bool'
                    }
                }
            }

        }
    },
    'correction': {
        'sampleUsed': {
            'type': 'string'
        },
        'curve': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'x': 'double',
                    'y': 'double'
                }
            }
        }
    },

    'required': ['sample', 'results', 'time', 'correction']
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
    return x.submit(data, "result")


def create(event, context):
    """
        creates a new sample result object, from a html api request

        :param event:
        :param context:
        :return:
    """

    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")

    data = json.loads(event['body'])

    return triggerEvent(data)

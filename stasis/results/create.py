from stasis.service.Queue import Queue
import time
import simplejson as json
from jsonschema import validate

# defines the schema of the incoming data object
dataSchema = {
    'sample': {
        'type': 'string'
    },
    'time': {
        'type': 'integer'
    },
    'correction': {
        'polynomial': {
            'type': 'integer'
        },
        'sampleUsed': {
            'type': 'string'
        },
        'curve': {
            'type': 'array',
            'items': {
                'type': 'object',
                'x': {
                    'type': 'number'
                },
                'y': {
                    'type': 'number'
                }
            }
        },
        'required':['polinomial', 'sampleUsed', 'curve']
    },
    'injections': {
        'type': 'object',
        'patterProperties': {
            '^.*$': {
                'type': 'object',
                'results': {
                   'type': 'array',
                   'items': {
                       'type': 'object',
                       'target': {
                           'retentionIndex': {
                               'type': 'number'
                           },
                           'name': {
                               'type': 'string'
                           },
                           'id': {
                               'type': 'string'
                           },
                           'mass': {
                               'type': 'number'
                           }
                       },
                       'annotation': {
                           'retentionIndex': {
                               'type': 'number'
                           },
                           'intensity': {
                               'type': 'integer'
                           },
                           'replaced': {
                               'type': 'boolean'
                           },
                           'mass': {
                               'type': 'number'
                           }
                       }
                   }
               }
            }
        }
    },

    'required': ['sample', 'time', 'correction', 'injections']
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

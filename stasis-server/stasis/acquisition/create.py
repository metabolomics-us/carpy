import time

import simplejson as json
from boto.dynamodb2.exceptions import ValidationException
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __ACQUISITION_SCHEMA__
from stasis.service.Status import Status
from stasis.tables import TableManager
from stasis.util.minix_parser import parse_minix_xml


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample
    :return: a serialized version of the submitted message
    """
    print("trigger event: " + json.dumps(data))
    saved = {}

    try:
        validate(data, __ACQUISITION_SCHEMA__)

        timestamp = int(time.time() * 1000)
        data['time'] = timestamp
        data['id'] = data['sample']

        # put item in table instead of queueing
        tm = TableManager()
        acqtable = tm.get_acquisition_table()
        trktable = tm.get_tracking_table()

        data = tm.sanitize_json_for_dynamo(data)
        saved = acqtable.put_item(Item=data)  # save or update our item

        # add 'entered' tracking status
        tracking = {
            'id': data['id'],
            'experiment': data['experiment'] if data['experiment'] != None else 'unknown',
            'sample': data['sample'],
            'status': [{
                'time': data['time'],
                'value': 'entered',
                'priority': Status().priority('entered')
            }]
        }
        tracked = trktable.put_item(Item=tracking)

    except ValidationException as vex:
        data = str(vex.body)
        saved['ResponseMetadata']['HTTPStatusCode'] = 400
    except Exception as ex:
        data = str(ex)
        saved['ResponseMetadata']['HTTPStatusCode'] = 500

    return {
        'body': json.dumps(data),
        'statusCode': saved['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__
    }


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

    response = []
    for x in parse_minix_xml(data['url']):
        # rederict to the appropriate functions
        response.append(triggerEvent(x))

    return response

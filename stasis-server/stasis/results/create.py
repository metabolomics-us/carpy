import os
import time

import simplejson as json
from jsonschema import validate

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __RESULT_SCHEMA__
from stasis.service.Bucket import Bucket
from stasis.tables import TableManager


def triggerEvent(data):
    """
        submits the given data to the queue

    :param data: requires sample
    :return: a serialized version of the submitted message
    """

    print("trigger event: %s" % data)

    validate(data, __RESULT_SCHEMA__)

    timestamp = int(time.time() * 1000)
    data['time'] = timestamp
    data['id'] = data['sample']

    if 'sample' in data:
        table = Bucket(os.environ['resultTable'])

        existing = table.exists(data['id'])

        if existing:
            existing = json.loads(table.load(data['id']))
            # need to append and/or update result to injections
            data['injections'] = {**existing['injections'], **data['injections']}

        result = table.save(data['id'], json.dumps(TableManager().sanitize_json_for_dynamo(data)))

        return {
            'body': json.dumps(data),
            'statusCode': result['ResponseMetadata']['HTTPStatusCode'],
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }
    else:
        return {
            'body': json.dumps({'error': 'no sample provided'}),
            'statusCode': 400,
            'isBase64Encoded': False,
            'headers': __HTTP_HEADERS__
        }


def create(event, context):
    """
        creates a new sample result object, from a html api request

        :param event:
        :param context:
        :return:
    """

    print(event)

    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")

    data = json.loads(event['body'])

    return triggerEvent(data)

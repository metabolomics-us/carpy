import time

import simplejson as json
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __TARGET_SCHEMA__
from stasis.tables import TableManager


def create(event, context):
    """
        creates and submits a new target to the table

        :param event:
        :param context:
        :return: a serialized version of the submitted message
    """
    if 'body' not in event:
        raise Exception("please ensure you provide a valid body")
    data = json.loads(event['body'])

    try:
        print("data for event triggering: %s" % data)
        validate(data, __TARGET_SCHEMA__)
    except ValidationError as ve:
        return {
            'body': 'Error: %s' % str(ve),
            'statusCode': 422,
            'headers': __HTTP_HEADERS__
        }

    tm = TableManager()

    data['mz'], data['rt'] = data['mz_rt'].split("_")

    timestamp = int(time.time() * 1000)
    newTarget = {
        'method': data['method'],
        'mz_rt': data['mz_rt'],
        'time': timestamp,
        'mz': data['mz'],
        'rt': data['rt'],
        'sample': data['sample']
    }

    # if 'splash' in data and data['splash']:  # failsafe for when we have MS1 (no splash)
    #     newTarget['splash'] = data['splash']

    newTarget = tm.sanitize_json_for_dynamo(newTarget)

    # put item in table
    saved = {}
    try:
        table = tm.get_target_table()
        saved = table.put_item(Item=newTarget)
    except Exception as e:
        print("ERROR: %s" % str(e))
        newTarget = {}
        saved['ResponseMetadata']['HTTPStatusCode'] = 500

    return {
        'body': json.dumps(newTarget),
        'statusCode': saved['ResponseMetadata']['HTTPStatusCode'],
        'headers': __HTTP_HEADERS__
    }

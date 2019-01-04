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
        # print("data for event triggering: %s" % data)
        validate(data, __TARGET_SCHEMA__)
    except ValidationError as ve:
        return {
            'body': json.dumps({'error': str(ve.message)}),
            'statusCode': 422,
            'headers': __HTTP_HEADERS__
        }

    tm = TableManager()

    timestamp = int(time.time() * 1000)
    data['name'] = 'Unknown' if 'name' not in data or data['name'] == '' else data['name']
    data['riMarker'] = False if 'riMarker' not in data else data['riMarker']
    data['rtUnit'] = 'seconds' if 'rtUnit' not in data else data['rtUnit']
    data['mz_rt'] = f'{data["mz"]}_{data["rt"]}'
    data['time'] = timestamp

    # if 'splash' in data and data['splash']:  # failsafe for when we have MS1 (no splash)
    #     newTarget['splash'] = data['splash']

    newTarget = tm.sanitize_json_for_dynamo(data)

    # put item in table
    saved = {}
    try:
        table = tm.get_target_table()
        saved = table.put_item(Item=newTarget)
        print('target created')
        return {
            'body': json.dumps(newTarget),
            'statusCode': 200,
            'headers': __HTTP_HEADERS__
        }
    except Exception as e:
        print("ERROR creating target: %s" % str(e))
        return {
            'body': json.dumps({'error': str(e)}),
            'statusCode': 500,
            'headers': __HTTP_HEADERS__
        }

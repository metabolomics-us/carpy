import time

import simplejson as json
from boto3.dynamodb.conditions import Key
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __TARGET_SCHEMA__
from stasis.tables import TableManager


def update(event, context):
    if 'body' not in event or not event['body']:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'error': 'missing target\'s method and/or mz_rt, please provide these values in body'})
        }

    print('EVENT: %s' % event)
    try:
        data = json.loads(event['body'])
        print('DATA: ', json.dumps(data, indent=2))

        timestamp = int(time.time() * 1000)
        data['time'] = timestamp
    except Exception as ex:
        print(str(ex))
        raise

    keys = all(x in data for x in ['method', 'mz_rt'])
    if not keys:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'error': 'missing target\'s method and/or mz_rt, please provide these values in body'})
        }

    try:
        print("data for event triggering: %s" % data)
        validate(data, __TARGET_SCHEMA__)
    except ValidationError as ve:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'error': '%s' % str(ve)})
        }

    tm = TableManager()
    try:
        tgt_table = tm.get_target_table()
        existing = tgt_table.query(
            KeyConditionExpression=
            Key('method').eq(data['method']) &
            Key('mz_rt').eq(data['mz_rt'])
        )
    except Exception as e:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'error': 'error querying target. %s ' % str(e)})
        }

    if not existing['Items']:
        return {
            'statusCode': 404,
            'headers': __HTTP_HEADERS__,
            'body': json.dumps({'error': 'Target not found'})
        }
    else:
        try:
            data = tm.sanitize_json_for_dynamo(data)
            data = dict(existing, **data)
            tgt_table.put_item(Item=data)

            return {
                'statusCode': 200,
                'headers': __HTTP_HEADERS__,
                'body': json.dumps(data)
            }
        except Exception as ex:
            print("ERRROR update: %s" % str(ex))
            return {
                'statusCode': 500,
                'headers': __HTTP_HEADERS__,
                'body': json.dumps({'error': str(ex)})
            }

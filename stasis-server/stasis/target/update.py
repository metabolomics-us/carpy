import time

import simplejson as json
from jsonschema import validate, ValidationError

from stasis.headers import __HTTP_HEADERS__
from stasis.schema import __TARGET_SCHEMA__
from stasis.tables import TableManager


def update(event, context):
    print('received event: %s' % json.dumps(event, indent=2))

    if not event.get('body'):
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
            'body': json.dumps({'error': 'missing target\'s method and/or mz_rt, please provide these values in body'})
        }

    try:
        data = json.loads(event.get('body'))

        timestamp = int(time.time() * 1000)
        data['time'] = timestamp
    except Exception as ex:
        print(ex.args)
        raise

    print([x in data.keys() for x in ['method', 'mz_rt']])
    keys = all([x in data.keys() for x in ['method', 'mz_rt']])

    if not keys:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
            'body': json.dumps({'error': 'missing target\'s method and/or mz_rt, please provide these values in body'})
        }

    try:
        validate(data, __TARGET_SCHEMA__)
    except ValidationError as ve:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
            'body': json.dumps({'error': '%s' % str(ve)})
        }

    tm = TableManager()
    try:
        print('updating...')
        tgt_table = tm.get_target_table()
        existing = tgt_table.get_item(
            Key={'method': data['method'],
                 'mz_rt': data['mz_rt']}
        )
        existing = existing.get('Item')
    except Exception as e:
        return {
            'statusCode': 422,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
            'body': json.dumps({'error': 'error querying target. %s ' % str(e)})
        }

    if existing is None:
        return {
            'statusCode': 404,
            'headers': __HTTP_HEADERS__,
            'isBase64Encoded': False,
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
                'isBase64Encoded': False,
                'body': json.dumps(data)
            }
        except Exception as ex:
            print("ERROR update: %s" % str(ex))
            return {
                'statusCode': 500,
                'headers': __HTTP_HEADERS__,
                'isBase64Encoded': False,
                'body': json.dumps({'error': str(ex)})
            }

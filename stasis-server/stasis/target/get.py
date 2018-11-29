from urllib.parse import unquote

import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def get(events, context):
    """returns a list of targets for a specific method and if present an MZ_RT value"""
    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events:
        if 'method' in events['pathParameters']:
            tm = TableManager()
            table = tm.get_target_table()

            result = None

            if 'mz_rt' in events['pathParameters']:
                result = table.query(
                    KeyConditionExpression=
                    Key('method').eq(events['pathParameters']['method']) &
                    Key('mz_rt').eq(events['pathParameters']['mz_rt'])
                )
                print('MZRT QUERY: %s' % result['Items'])
            else:
                print("encoded: %s" % events['pathParameters']['method'])
                print("unencoded: %s" % unquote(events['pathParameters']['method']))
                result = table.query(
                    KeyConditionExpression=Key('method').eq(unquote(events['pathParameters']['method']))
                )
                print('METHOD QUERY: %s' % result['Items'])

            if 'Items' in result and len(result['Items']) > 0:
                # create a response when sample is found
                return {
                    'statusCode': 200,
                    'headers': __HTTP_HEADERS__,
                    'body': json.dumps({'targets': result['Items']})
                }
            else:
                print(result)
                # create a response when sample is not found
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "method not found"})
                }
        else:
            return {
                "statusCode": 422,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "library name is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

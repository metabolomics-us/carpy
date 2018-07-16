import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def get(events, context):
    """returns the specific sample from the storage"""
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
            else:
                result = table.query(
                    KeyConditionExpression=Key('method').eq(events['pathParameters']['method'])
                )

            if 'Items' in result and len(result['Items']) > 0:
                # create a response when sample is found
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(result['Items'][0])
                }
            else:
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

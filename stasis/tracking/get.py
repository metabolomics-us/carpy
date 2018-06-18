import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.service.Persistence import Persistence
from stasis.headers import __HTTP_HEADERS__
from stasis.tables import get_acquisition_table, get_tracking_table


def get(events, context):
    """returns the specific element from the storage"""

    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            table = get_tracking_table()

            result = table.query(
                KeyConditionExpression=Key('id').eq(events['pathParameters']['sample'])
            )

            print("query result was {}".format(result))

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
                    "body": json.dumps({"error": "sample not found"})
                }
        else:
            return {
                "statusCode": 422,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "sample name is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

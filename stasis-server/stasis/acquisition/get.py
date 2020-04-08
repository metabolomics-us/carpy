import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def get(events, context):
    """returns the specific element from the storage"""

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:
            tm = TableManager()
            table = tm.get_acquisition_table()
            sample = events['pathParameters']['sample']

            print("looking for sample: {}".format(sample))
            result = table.query(
                KeyConditionExpression=Key('id').eq(sample)
            )

            if "Items" in result and len(result['Items']) > 0:
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(result['Items'][0])
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "no sample found with this identifier : {}".format(
                        events['pathParameters']['sample'])})
                }
        else:
            return {
                "statusCode": 404,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "sample name is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

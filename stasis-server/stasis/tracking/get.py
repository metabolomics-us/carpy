import simplejson as json
from boto3.dynamodb.conditions import Key

from stasis.headers import __HTTP_HEADERS__
from stasis.tables import TableManager


def get(events, context):
    """returns the specific sample from the storage"""

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:
            tm = TableManager()
            table = tm.get_tracking_table()

            result = table.query(
                KeyConditionExpression=Key('id').eq(events['pathParameters']['sample'])
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


def get_experiment(events, context):
    """returns paged list with the latest status for the samples in the given experiment"""

    if 'pathParameters' in events:
        if 'experiment' in events['pathParameters']:
            expId = events['pathParameters']['experiment']

            if 'psize' in events['pathParameters']:
                page_size = int(events['pathParameters']['psize'])
            else:
                page_size = 25

            query_params = {
                'IndexName': 'experiment-id-index',
                'Select': 'ALL_ATTRIBUTES',
                'KeyConditionExpression': Key('experiment').eq(expId),
                'Limit': page_size
            }

            if 'lastSample' in events['pathParameters']:
                print(f"Not the first page // {events['pathParameters']['lastSample']}")
                query_params['ExclusiveStartKey'] = {
                    "experiment": expId,
                    "id": events['pathParameters']['lastSample']
                }

            tm = TableManager()
            table = tm.get_tracking_table()

            try:
                result = table.query(**query_params)
                items = result['Items']
                last_item = result['LastEvaluatedKey'] or ''

                data = {
                    'statusCode': 200,
                    'headers': __HTTP_HEADERS__,
                    'body': json.dumps({
                        "items": items,
                        "last_item": last_item
                    })
                }

                return data
            except Exception as ex:
                print("QUERY-ERROR: %s" % str(ex))
                return {
                    "statusCode": 418,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": ex.args})
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

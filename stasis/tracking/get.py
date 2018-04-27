from stasis.util import decimalencoder
import json
import os

import boto3

dynamodb = boto3.resource('dynamodb')


def get(events, context):
    """returns the specific element from the storage"""

    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            table = dynamodb.Table(os.environ["trackingTable"])
            result = table.get_item(
                Key={
                    'id': events['pathParameters']['sample']
                }
            )

            # create a response
            return {
                "statusCode": 200,
                "body": json.dumps(result['Item'],
                           cls=decimalencoder.DecimalEncoder)
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "sample name is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

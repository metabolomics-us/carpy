import os

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Bucket import Bucket


def get(events, context):
    """returns the specific element from the storage"""

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            db = Bucket(os.environ["resultTable"])

            if db.exists(events['pathParameters']['sample']):
                result = db.load(events['pathParameters']['sample'])

                # create a response
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                    "body": result
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps(events)
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

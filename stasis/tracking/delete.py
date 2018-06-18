import os

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Persistence import Persistence


def delete(events, context):
    """returns the specific element from the storage"""

    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events and 'delete' in events:
        if 'sample' in events['pathParameters']:

            db = Persistence(os.environ["trackingTable"])
            result = db.delete(events['pathParameters']['sample'])

            # create a response
            return {
                "statusCode": 204,
                "headers": __HTTP_HEADERS__,
                "body": ""
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

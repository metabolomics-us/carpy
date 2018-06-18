import simplejson as json
import os

from stasis.service.Persistence import Persistence
from stasis.headers import __HTTP_HEADERS__
from stasis.tables import get_tracking_table, get_acquisition_table


def get(events, context):
    """returns the specific element from the storage"""

    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            db = Persistence(get_acquisition_table())
            result = db.load(events['pathParameters']['sample'])

            # create a response
            return {
                "statusCode": 200,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps(result)
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

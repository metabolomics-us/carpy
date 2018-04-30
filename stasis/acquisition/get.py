import json
import os

from stasis.service.Persistence import Persistence
from stasis.util import decimalencoder


def get(events, context):
    """returns the specific element from the storage"""

    print("received event: " + json.dumps(events, indent=2))

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            db = Persistence(os.environ["acquisitionTable"])
            result = db.load(events['pathParameters']['sample'])

            # create a response
            return {
                "statusCode": 200,
                "body": json.dumps(result,
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

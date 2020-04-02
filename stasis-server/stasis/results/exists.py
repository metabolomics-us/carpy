import os

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Bucket import Bucket


def exist(events, context):
    """returns the specific element from the storage"""

    print(f'processed file check for bucket {os.environ["resultTable"]}')

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:

            sample = f"{events['pathParameters']['sample']}.json"
            db = Bucket(os.environ["resultTable"])

            print("looking for file: {}".format(sample))
            if db.exists(sample):
                # create a response
                return {
                    "statusCode": 200,
                    "headers": __HTTP_HEADERS__,
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                }
        else:
            return {
                "statusCode": 503,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "sample name is not provided!"})
            }
    else:
        return {
            "statusCode": 503,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

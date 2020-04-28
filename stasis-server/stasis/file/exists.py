import os

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Bucket import Bucket


def exists(events, context):
    """returns the existence status of a file on S3"""
    print(f'raw file check for bucket {os.environ["dataBucket"]}')

    if 'pathParameters' in events:
        if 'sample' in events['pathParameters']:
            data = Bucket(os.environ['dataBucket'])
            sample = events['pathParameters']['sample']
            print("looking for file: {}".format(sample))
            if data.exists(sample):
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

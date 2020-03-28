import json
import os

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Bucket import Bucket


def bucket_json(event, context):
    Bucket(bucket_name=os.environ.get('dataBucket'))
    return {
        "statusCode": 200,
        "headers": __HTTP_HEADERS__,
        "body": json.dumps({
            'name': os.environ.get('dataBucket')
        })
    }


def bucket_raw(event, context):
    Bucket(bucket_name=os.environ.get('dataBucket'))
    return {
        "statusCode": 200,
        "headers": __HTTP_HEADERS__,
        "body": json.dumps({
            'name': os.environ.get('dataBucket')
        })
    }


def bucket_zip(event, context):
    Bucket(bucket_name=os.environ.get('dataBucket'))
    return {
        "statusCode": 200,
        "headers": __HTTP_HEADERS__,
        "body": json.dumps({
            'name': os.environ.get('dataBucket')
        })
    }

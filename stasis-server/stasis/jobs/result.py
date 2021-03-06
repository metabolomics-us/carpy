import base64
import os
import traceback

import simplejson as json

from stasis.headers import __HTTP_HEADERS__
from stasis.service.Bucket import Bucket
from stasis.service.Status import AGGREGATED_AND_UPLOADED
from stasis.tables import get_job_state


def exist(events, context):
    """
    downloads a finished job results. This will be zipfile
    :param events:
    :param context:
    :return:
    """

    print(f'received event: {json.dumps(events, indent=2)} for bucket {os.environ["dataBucket"]}')

    if 'pathParameters' in events:
        if 'job' in events['pathParameters']:

            job = events['pathParameters']['job']
            db = Bucket(os.environ["dataBucket"])
            state: str = get_job_state(job)

            if state is None:
                return {
                    "statusCode": 503,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "job does not exist!", "job": job})
                }
            if state != AGGREGATED_AND_UPLOADED:
                return {
                    "statusCode": 503,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "job not ready yet!", "job": job, "state": state,
                                        "required_state": AGGREGATED_AND_UPLOADED})
                }
            filename = "{}.zip".format(job)

            if db.exists(filename):
                try:
                    # create a response
                    return {
                        "statusCode": 200,
                        "headers": __HTTP_HEADERS__,
                    }
                except Exception as e:
                    traceback.print_exc()
                    return {
                        "statusCode": 503,
                        "headers": __HTTP_HEADERS__,
                        "body": json.dumps({
                            "error": str(e),
                            "job": job
                        })
                    }

            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({'error': "not able to find job", "filename": filename, "job": job})
                }
        else:
            return {
                "statusCode": 404,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "job is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }


def get(events, context):
    """
    downloads a finished job results. This will be zipfile
    :param events:
    :param context:
    :return:
    """

    if 'pathParameters' in events:
        if 'job' in events['pathParameters']:

            job = events['pathParameters']['job']

            state: str = get_job_state(job)

            if state is None:
                return {
                    "statusCode": 503,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "job does not exist!", "job": job})
                }
            if state != AGGREGATED_AND_UPLOADED:
                return {
                    "statusCode": 503,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({"error": "job not ready yet!", "job": job, "state": state,
                                        "required_state": AGGREGATED_AND_UPLOADED})
                }
            db = Bucket(os.environ["dataBucket"])

            filename = "{}.zip".format(job)

            if db.exists(filename):
                try:
                    content = base64.b64encode(db.load(filename, binary=True)).decode("utf-8")
                    # create a response
                    return {
                        "statusCode": 200,
                        "headers": __HTTP_HEADERS__,
                        "body": json.dumps({
                            "content": content,
                            "job": job
                        })
                    }
                except Exception as e:
                    traceback.print_exc()
                    return {
                        "statusCode": 503,
                        "headers": __HTTP_HEADERS__,
                        "body": json.dumps({
                            "error": str(e),
                            "job": job
                        })
                    }

            else:
                return {
                    "statusCode": 404,
                    "headers": __HTTP_HEADERS__,
                    "body": json.dumps({'error': "not able to find job", "filename": filename, "job": job})
                }
        else:
            return {
                "statusCode": 404,
                "headers": __HTTP_HEADERS__,
                "body": json.dumps({"error": "job is not provided!"})
            }
    else:
        return {
            "statusCode": 404,
            "headers": __HTTP_HEADERS__,
            "body": json.dumps({"error": "not supported, need's be called from a http event!"})
        }

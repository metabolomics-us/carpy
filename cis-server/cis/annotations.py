import sys
import traceback
import urllib.parse

import simplejson as json

from loguru import logger
from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="annotations", level="INFO", backtrace=False,
           diagnose=False)


def get_all(events, context):
    """
    queries the database for a paged list of annotations associated with a target.
    :param events: the Lambda "event" object with pathParameters and queryStrings to run the query.

    :param context: unused
    :return: an dictionary to be converted in a response by AWS APIGateway.

    """
    logger.info(f'EVENTS: {events}')

    if not 'queryStringParameters' in events:
        limit = 50
        offset = 0
    else:
        if 'limit' in events['queryStringParameters']:
            limit = int(events['queryStringParameters']['limit'])
        if 'offset' in events['queryStringParameters']:
            offset = int(events['queryStringParameters']['offset'])

    if 'pathParameters' in events:
        if 'splash' in events['pathParameters']:
            splash = urllib.parse.unquote(events['pathParameters']['splash'])

            # get the annotations count and the target_id for the given splash
            response = database.query(
                'SELECT COUNT(*), pt."id" FROM "pgspectra" ps join "pgtarget" pt ON ps."target_id" = pt."id" '
                'WHERE pt."splash" = %s GROUP BY pt."id"',
                conn, [splash])
            count, tgtid = response[0]

            if count == 0:
                return {
                    "statusCode": 404,
                    "body": {}
                }
            else:
                try:
                    transform = lambda x: {
                        "id": x[0],
                        "accurate_mass": x[1],
                        "ion_mode": x[2],
                        "ms_level": x[3],
                        "original_retention_time": x[4],
                        "precursor_mass": x[5],
                        "raw_spectrum": x[6],
                        "replaced": x[7],
                        "retention_index": x[8],
                        "spectrum": x[9],
                        "splash": x[10],
                        "sample_id": x[11],
                        "target_id": x[12]
                    }
                    response = database.html_response_query(
                        'SELECT * FROM "pgspectra" ps WHERE "target_id" = %s '
                        f'LIMIT {limit} OFFSET {offset}',
                        conn, [tgtid], transform)

                    result = json.loads(response['body'])

                    # create a response
                    body_data = json.dumps({
                            "splash": splash,
                            "total_count": count,
                            "annotations": result
                        }, use_decimal=True)
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": body_data
                    }
                except Exception as e:
                    # traceback.print_exc()
                    return {
                        "statusCode": 500,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "error": str(e),
                            "splash": splash
                        })
                    }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a target's splash"
                })
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            })
        }

import sys
import traceback
import urllib.parse

import simplejson as json
from loguru import logger

from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="libraries", level="INFO", backtrace=True,
           diagnose=True)


def libraries(event, context):
    transform = lambda x: x[0]

    sql = "SELECT \"id\" FROM public.pgmethod"
    return database.html_response_query(sql=sql, connection=conn, transform=transform)


def delete(event, context):
    if 'pathParameters' in event:
        if 'library' in event['pathParameters']:
            method_name = urllib.parse.unquote(event['pathParameters']['library'])

            result = database.query(
                "DELETE FROM pgtarget pt where \"method_id\" = (%s)", conn, [method_name])

            try:
                # create a response
                return {
                    "statusCode": 200,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "library": method_name
                    }, use_decimal=True)
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    }, use_decimal=True)
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }


def size(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.html_response_query(
                "SELECT count(*), \"target_type\" FROM pgtarget pt "
                "WHERE dtype = 'PgInternalTarget' AND \"method_id\" = %s "
                "GROUP BY target_type",
                conn, [method_name])

            try:
                # create a response
                return result
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    }, use_decimal=True)
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.query(
                "SELECT exists (SELECT 1 FROM pgmethod pt WHERE \"id\" = (%s) LIMIT 1)", conn, [method_name])

            try:
                # create a response
                return {
                    "statusCode": 200,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "exists": result[0][0],
                        "library": method_name
                    }, use_decimal=True)
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    }, use_decimal=True)
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }

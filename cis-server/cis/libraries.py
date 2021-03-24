import json
import sys
import traceback
import urllib.parse

from loguru import logger
from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="libraries", level="INFO", backtrace=True,
           diagnose=True)


@logger.catch
def libraries(event, context):
    transform = lambda x: x[0]

    sql = "SELECT \"id\" FROM public.pgmethod"
    return database.html_response_query(sql=sql, connection=conn, transform=transform)


@logger.catch
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
                    })
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
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


@logger.catch
def size(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.html_response_query(
                "SELECT count(*), pt.target_type FROM pgtarget pt WHERE dtype = 'PgInternalTarget' and \"method_id\" = (%s) group by target_type",
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
                    })
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
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


@logger.catch
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
                    })
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name"
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

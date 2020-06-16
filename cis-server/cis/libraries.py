import json
import traceback
import urllib.parse

from cis import database, headers

conn = database.connect()


def libraries(event, context):
    transform = lambda x: x[0]

    sql = "SELECT \"method\" FROM public.pg_target group by \"method\""
    return database.html_response_query(sql=sql, connection=conn, transform=transform)


def delete(event, context):
    if 'pathParameters' in event:
        if 'library' in event['pathParameters']:
            method_name = urllib.parse.unquote(event['pathParameters']['library'])

            result = database.query(
                "DELETE FROM pg_target pt where \"method\" = (%s)", conn, [method_name])

            try:
                # create a response
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "library": method_name
                    })
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "headers": headers.__HTTP_HEADERS__,
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "headers": headers.__HTTP_HEADERS__,
                    "error": "you need to provide a 'library' name"
                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "headers": headers.__HTTP_HEADERS__,
                "error": "missing path parameters"
            })
        }


def size(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.html_response_query(
                "SELECT count(*), pt.target_type FROM pg_target pt WHERE \"method\" = (%s) group by target_type", conn, [method_name])

            try:
                # create a response
                return result
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "headers": headers.__HTTP_HEADERS__,
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "headers": headers.__HTTP_HEADERS__,
                    "error": "you need to provide a 'library' name"
                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "headers": headers.__HTTP_HEADERS__,
                "error": "missing path parameters"
            })
        }


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.query(
                "SELECT exists (SELECT 1 FROM pg_target pt WHERE \"method\" = (%s) LIMIT 1)", conn, [method_name])

            try:
                # create a response
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "headers": headers.__HTTP_HEADERS__,
                        "exists": result[0][0],
                        "library": method_name
                    })
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "headers": headers.__HTTP_HEADERS__,
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "headers": headers.__HTTP_HEADERS__,
                    "error": "you need to provide a 'library' name"
                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "headers": headers.__HTTP_HEADERS__,
                "error": "missing path parameters"
            })
        }

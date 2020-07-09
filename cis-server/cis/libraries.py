import json
import traceback
import urllib.parse

from cis import database, headers

conn = database.connect()


def libraries(event, context):
    transform = lambda x: x[0]

    sql = "SELECT \"method\" FROM public.pgtarget where dtype = 'PgInternalTarget' group by \"method\""
    return database.html_response_query(sql=sql, connection=conn, transform=transform)


def delete(event, context):
    if 'pathParameters' in event:
        if 'library' in event['pathParameters']:
            method_name = urllib.parse.unquote(event['pathParameters']['library'])

            result = database.query(
                "DELETE FROM pgtarget pt where dtype = 'PgInternalTarget' and \"method\" = (%s)", conn, [method_name])

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


def size(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.html_response_query(
                "SELECT count(*), pt.target_type FROM pgtarget pt WHERE dtype = 'PgInternalTarget' and \"method\" = (%s) group by target_type", conn, [method_name])

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


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])

            result = database.query(
                "SELECT exists (SELECT 1 FROM pgtarget pt WHERE dtype = 'PgInternalTarget' and \"method\" = (%s) LIMIT 1)", conn, [method_name])

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

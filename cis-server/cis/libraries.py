import json
import traceback
import urllib.parse

from cis import database

conn = database.connect()


def libraries(event, context):
    transform = lambda x: x[0]

    sql = "SELECT \"method\" FROM public.pg_target group by \"method\""
    return database.html_response_query(sql=sql, connection=conn, transform=transform)


def delete(event, context):
    pass


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
                        "exists": result[0][0],
                        "library": method_name
                    })
                }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    })
                }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name",

                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "missing path parameters",

            })
        }

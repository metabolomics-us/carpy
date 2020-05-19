import json
import traceback

from cis import database

conn = database.connect()


def libraries(event, context):
    try:
        result = database.query("SELECT \"method\" FROM public.pg_target group by \"method\"", conn)

        result = list(map(lambda x: x[0], result))
        # create a response
        return {
            "statusCode": 200,
            "body": json.dumps(
                result
            )
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
            })
        }


def delete(event, context):
    pass


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters']:

            method_name = events['pathParameters']['library']

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

import json
import traceback
import urllib.parse

from cis import database, headers

try:
    conn = database.connect()
except Exception as e:
    print(str(e))
    exit(1)


def create_server_error(method, value, msg):
    return {
        "statusCode": 500,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "error": msg,
            "method": method,
            "value": value
        })
    }


def create_not_found(msg):
    return {
        "statusCode": 404,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "error": msg
        })
    }


def profiles(events, context):
    print(f"EVENT: {events}")

    if 'pathParameters' in events:
        if 'method' in events['pathParameters']:
            method = events['pathParameters']['method']

            if method not in ['target', 'sample']:
                return create_server_error(method, None, "invalid object type, it should be <target|sample>")

            if 'value' in events['pathParameters']:

                value = urllib.parse.unquote(events['pathParameters']['value'])

                sql = f'SELECT "id", "name" FROM public.pgprofile WHERE (%s) = (%s)'

                try:
                    result = database.query(sql, conn, [f'{method}_id', value])
                    print(f'RESULT: {result}')
                    # create a response
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "profiles": result,
                            "method": method,
                            "value": value
                        })
                    }
                except Exception as ex:
                    traceback.print_exc()
                    return create_server_error(method, value, ex)
            else:
                return create_server_error(method, None, f'missing {method}_id')
        else:
            return create_server_error(None, None, 'missing object type to query <target|sample>')
    else:
        return create_server_error(None, None, 'missing path parameters')


def config(events, context):
    yield

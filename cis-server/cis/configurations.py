import inspect
import sys
import traceback
import urllib.parse

import simplejson as json
from loguru import logger

from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="configurations", level="INFO", backtrace=True,
           diagnose=True)


def create_server_error(method, value, msg):
    return {
        "statusCode": 500,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "error": msg,
            "method": method,
            "value": value
        }, use_decimal=True)
    }


def create_not_found(msg):
    return {
        "statusCode": 404,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "error": msg
        }, use_decimal=True)
    }


def profiles(events, context):
    query = 'SELECT "id", "name" FROM public.pgprofile WHERE @filter_field@ = %s'
    return process_event(events, query)


def configs(events, context):
    query = 'SELECT "id", "name", "value", "data_type", "declared_in" ' \
            'FROM public.pgconfiguration WHERE @filter_field@ = %s'
    return process_event(events, query)


def process_event(events, query_str):
    if 'pathParameters' in events:
        if 'method' in events['pathParameters']:
            method = events['pathParameters']['method']
            filter_field = f'{method}_id'

            if method not in ['target', 'sample']:
                return create_server_error(method, None, "invalid object type, it should be <target|sample>")

            if 'value' in events['pathParameters']:

                value = urllib.parse.unquote(events['pathParameters']['value'])

                query = query_str.replace('@filter_field@', filter_field)

                try:
                    caller = inspect.stack()[1][3]
                    result = database.query(query, conn, [value])
                    # create a response
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            caller: result,
                            "method": method,
                            "value": value
                        }, use_decimal=True)
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

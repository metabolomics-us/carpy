import json

from cis import database

conn = database.connect()


def all(events, context):
    if 'pathParameters' in events:
        if 'offset' in events['pathParameters']:
            offset = events['pathParameters']['offset']
        else:
            offset = 0
        if 'limit' in events['pathParameters']:
            limit = events['pathParameters']['limit']
        else:
            limit = 10

        if 'library' in events['pathParameters']:

            method_name = events['pathParameters']['library']
            transform = lambda x: x[0]
            sql = "SELECT splash  FROM public.pg_target where \"method\" = %s limit %s offset %s  "
            return database.html_response_query(sql=sql, connection=conn, transform=transform, params=[method_name,limit,offset])
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


def delete(events, context):
    pass


def exists(events, context):
    pass

import json
import traceback
import urllib.parse

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

            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            print(f"loading all compounds for: {method_name} limit {limit} and offset {offset}")
            transform = lambda x: x[0]
            sql = "SELECT splash  FROM public.pg_target where \"method\" = %s limit %s offset %s  "
            return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                params=[method_name, limit, offset])
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


def get(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])

            transform = lambda x: {
                'id': x[0],
                'accurate_mass': x[1],
                'confirmed': x[2],
                'inchi_key': x[3],
                'matrix': x[4],
                'method': x[6],
                'ms_level': x[7],
                'required_for_correction': x[9],
                'retention_index': x[10],
                'retention_index_standard': x[11],
                'sample': x[12],
                'spectrum': x[13],
                'splash': x[14],
                'name': x[15],
                'unique_mass': x[16],
                'precursor_mass': x[17]
            }
            result = database.html_response_query(
                "SELECT id, accurate_mass, confirmed, inchi_key, matrix, members, \"method\", ms_level, raw_spectrum, required_for_correction, retention_index, retention_index_standard, sample_name, spectrum, splash, target_name, unique_mass, precursor_mass FROM pg_target pt WHERE \"method\" = (%s) and \"splash\" = (%s)",
                conn, [method_name, splash], transform=transform)

            return result
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name and a splash",

                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "missing path parameters",

            })
        }


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            result = database.query(
                "SELECT exists (SELECT 1 FROM pg_target pt WHERE \"method\" = (%s) and \"splash\" = (%s) LIMIT 1)",
                conn, [method_name, splash])

            try:
                # create a response
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "exists": result[0][0],
                        "library": method_name,
                        "splash": splash
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
                    "error": "you need to provide a 'library' name and a splash",

                })
            }
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "missing path parameters",

            })
        }

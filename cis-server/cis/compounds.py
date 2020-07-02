import json
import traceback
import urllib.parse

from cis import database, headers

conn = database.connect()


def has_members(events, context):
    """
    does this given bin has several members
    :param events:
    :param context:
    :return:
    """

    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            result = database.query(
                "SELECT count(*) FROM public.pg_internal_target_members a, pgtarget b where b.splash = (%s) and b.\"method\" = (%s)",
                conn, [splash, method_name])

            try:
                if result[0][0] > 0:
                    # create a response
                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "headers": headers.__HTTP_HEADERS__,
                            "members": True,
                            "count": result[0][0],
                            "library": method_name,
                            "splash": splash
                        })
                    }
                else:
                    return {
                        "statusCode": 404,
                        "body": json.dumps({
                            "headers": headers.__HTTP_HEADERS__,
                            "members": False,
                            "count": result[0][0],
                            "library": method_name,
                            "splash": splash
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
                    "error": "you need to provide a 'library' name and a splash"
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


def get_members(events, context):
    """
    return all members for this given bin
    :param events:
    :param context:
    :return:
    """
    if 'pathParameters' in events:
        if 'offset' in events['pathParameters']:
            offset = events['pathParameters']['offset']
        else:
            offset = 0
        if 'limit' in events['pathParameters']:
            limit = events['pathParameters']['limit']
        else:
            limit = 10

        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:

            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            print(f"loading all compounds for: {method_name} and splash {splash} limit {limit} and offset {offset}")
            transform = lambda x: x[0]
            sql = "SELECT members FROM public.pgtarget a, pg_internal_target_members b where a.id = b.pg_internal_target_id and  \"method\" = %s and splash = %s limit %s offset %s  "
            return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                params=[method_name, splash, limit, offset])
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name",

                })
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters",

            })
        }


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

            if 'type' in events['pathParameters']:

                target_type = events['pathParameters']['type']
                sql = "SELECT splash  FROM public.pgtarget where \"method\" = %s and target_type = %s and dtype = 'PgInternalTarget'  limit %s offset %s  "
                return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                    params=[method_name, target_type, limit, offset])
            else:
                sql = "SELECT splash  FROM public.pgtarget where \"method\" = %s and dtype = 'PgInternalTarget' limit %s offset %s  "
                return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                    params=[method_name, limit, offset])

        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name",

                })
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
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
                'target_type': x[2],
                'inchi_key': x[3],
                'method': x[4],
                'ms_level': x[5],
                'required_for_correction': x[7],
                'retention_index': x[8],
                'sample': x[9],
                'spectrum': x[10],
                'splash': x[11],
                'name': x[12],
                'unique_mass': x[13],
                'precursor_mass': x[14]
            }
            result = database.html_response_query(
                "SELECT id, accurate_mass, target_type, inchi_key, \"method\", ms_level, raw_spectrum, required_for_correction, retention_index, sample_name, spectrum, splash, target_name, unique_mass, precursor_mass FROM pgtarget pt WHERE \"method\" = (%s) and \"splash\" = (%s) and dtype='PgInternalTarget'",
                conn, [method_name, splash], transform=transform)

            return result
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "headers": headers.__HTTP_HEADERS__,
                    "error": "you need to provide a 'library' name and a splash"
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
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            result = database.query(
                "SELECT exists (SELECT 1 FROM pgtarget pt WHERE \"method\" = (%s) and \"splash\" = (%s) and dtype = 'PgInternalTarget' LIMIT 1)",
                conn, [method_name, splash])

            if result[0][0] == 0:
                return {
                    "statusCode": 404,
                }
            else:
                try:
                    # create a response
                    return {
                        "statusCode": 200,
                        "body": json.dumps({
                            "headers": headers.__HTTP_HEADERS__,
                            "exists": result[0][0],
                            "library": method_name,
                            "splash": splash
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
                    "error": "you need to provide a 'library' name and a splash"
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

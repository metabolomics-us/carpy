import json
import traceback
import urllib.parse

from cis import database, headers

conn = database.connect()


def register_name(events, context):
    """
    registers a new name for a given target
    :param events:
    :param context:
    :return:
    """

    splash = events['pathParameters']['splash']
    library = events['pathParameters']['library']
    identifiedBy = events['pathParameters']['identifiedBy']
    name = events['pathParameters']['name']

    # load compound to get the correct id
    result = database.query(
        "select p.id as \"target_id\", pn.id as \"name_id\" from pgtarget p , pgtarget_name pn, pgtarget_names pn2 where p.id = pn2.pg_internal_target_id and pn2.names_id  = pn.id and splash = (%s) and \"method\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s",
        conn, [splash, library, name, identifiedBy])

    if result is None:
        result = database.query(
            "select p.id from pgtarget p where splash = (%s) and \"method\" = (%s)",
            conn, [splash, library])

        if len(result) > 0:
            id = result[0][0]
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "headers": headers.__HTTP_HEADERS__,
                    "library": library,
                    "splash": splash
                })
            }
    elif len(result) > 0:
        id = result[0][0]

        for row in result:
            name_id = row[1]

            # drop references with this id = name + identifier

            result = database.query(
                "delete from pgtarget_names  where names_id  = %s",
                conn, [name_id])
            result = database.query(
                "delete from pgtarget_name  where id  = %s",
                conn, [name_id])

    # now register the given name and associated information
    # 1. get new sequence number
    result = database.query("select nextval('hibernate_sequence')", conn)

    newNameId = result[0][0]

    result = database.query(
        "insert into pgtarget_name(\"id\",\"name\",\"identified_by\",\"comment\") values(%s,%s,%s,%s)",
        conn, [newNameId, name, identifiedBy, ''])
    result = database.query("insert into pgtarget_names(\"names_id\",\"pg_internal_target_id\") values(%s,%s)",
                            conn,
                            [newNameId, id])
    # create a response
    return {
        "statusCode": 200,
        "body": json.dumps({
            "headers": headers.__HTTP_HEADERS__,
            "members": True,
            "library": library,
            "splash": splash
        })
    }


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
                'preferred_name': x[12],
                'associated_names': list(
                    map(lambda y: {'name': y[1], 'identifiedBy': y[0], 'comment': y[2]}, database.query(
                        "select pn.identified_by , pn.\"name\" , pn.\"comment\" from pgtarget p , pgtarget_name pn, pgtarget_names pn2 where p.id = pn2.pg_internal_target_id and pn2.names_id  = pn.id and p.id = %s",
                        conn, [x[0]]))),
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

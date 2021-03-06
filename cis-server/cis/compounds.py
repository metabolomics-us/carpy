import sys
import traceback
import urllib.parse

import simplejson as json
from loguru import logger

from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="compounds", level="INFO", backtrace=True,
           diagnose=True)


def register_comment(events, context):
    """
    registers a new comment for a given target.
    :param events:
    :param context:
    :return:
    """
    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    comment = events['body']

    logger.info(f"{splash} - {library} - {identifiedBy} - {comment}")

    # load compound AND comments to get the correct id
    result = database.query(
        'select p.id as "target_id", pn.id as "name_id" from pgtarget p, pgtarget_comment pn '
        'where p.id = pn.target_id and splash = %s and "method_id" = %s and "identified_by" = %s',
        conn, [splash, library, identifiedBy])

    # no compound with comments, find just compound
    if result is None:
        result = database.query(
            'select p.id from pgtarget p where splash = %s and "method_id" = %s',
            conn, [splash, library])

        if result is not None and len(result) > 0:
            id = result[0][0]
        else:
            return {
                "statusCode": 404,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "library": library,
                    "splash": splash
                }, use_decimal=True)
            }
    else:
        id = result[0][0]

    # now register the given name and associated information
    # 1. get new sequence number
    result = database.query("select nextval('hibernate_sequence')", conn)

    newNameId = result[0][0]

    result = database.query(
        'insert into pgtarget_comment("id","identified_by","comment","target_id") values(%s,%s,%s,%s)',
        conn, [newNameId, identifiedBy, comment, id])

    # create a response
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "members": True,
            "library": library,
            "splash": splash
        }, use_decimal=True)
    }


def delete_comments(events, context):
    splash = events['pathParameters']['splash']
    library = events['pathParameters']['library']

    result = database.query(
        "select distinct p.id from pgtarget p , pgtarget_comment pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s)",
        conn, [splash, library])

    if result is not None:

        for row in result:
            database.query(
                "delete from pgtarget_comment  where id  = %s",
                conn, [row[0]])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }
    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }


def delete_adducts(events, context):
    splash = events['pathParameters']['splash']
    library = events['pathParameters']['library']

    result = database.query(
        "select distinct p.id from pgtarget p , pgtarget_adduct pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s)",
        conn, [splash, library])

    if result is not None:

        for row in result:
            database.query(
                "delete from pgtarget_adduct  where id  = %s",
                conn, [row[0]])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }
    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }


def delete_names(events, context):
    splash = events['pathParameters']['splash']
    library = events['pathParameters']['library']

    result = database.query(
        "select distinct p.id from pgtarget p , pgtarget_name pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s)",
        conn, [splash, library])

    if result is not None:

        for row in result:
            database.query(
                "delete from pgtarget_name  where target_id  = %s",
                conn, [row[0]])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }
    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }


def register_adduct(events, context):
    """
    registers a new adduct for a given target
    :param events:
    :param context:
    :return:
    """
    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    name = urllib.parse.unquote(events['pathParameters']['name'])
    comment = events.get('body', '')

    logger.info(f"{splash} - {library} - {identifiedBy} - {name}")
    # load compound to get the correct id
    result = database.query(
        "select p.id as \"target_id\", pn.id as \"name_id\" from pgtarget p , pgtarget_adduct pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s",
        conn, [splash, library, name, identifiedBy])

    if result is None:
        result = database.query(
            "select p.id from pgtarget p where splash = (%s) and \"method_id\" = (%s)",
            conn, [splash, library])

        if result is not None and len(result) > 0:
            id = result[0][0]
        else:
            return {
                "statusCode": 404,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "library": library,
                    "splash": splash
                }, use_decimal=True)
            }
    elif len(result) > 0:
        id = result[0][0]

        for row in result:
            name_id = row[1]

            result = database.query(
                "delete from pgtarget_adduct  where id = %s",
                conn, [name_id])

    # now register the given name and associated information
    # 1. get new sequence number
    result = database.query("select nextval('hibernate_sequence')", conn)

    newNameId = result[0][0]

    result = database.query(
        "insert into pgtarget_adduct(\"id\",\"name\",\"identified_by\",\"comment\",\"target_id\") values(%s,%s,%s,%s,%s)",
        conn, [newNameId, name, identifiedBy, comment, id])
    # create a response
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "members": True,
            "library": library,
            "splash": splash
        }, use_decimal=True)
    }


def delete_adduct(events, context):
    """

    :param events:
    :param context:
    :return:
    """

    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    name = urllib.parse.unquote(events['pathParameters']['name'])

    result = database.query(
        "select distinct pn.id from pgtarget p , pgtarget_adduct pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s",
        conn, [splash, library, name, identifiedBy])

    if result is not None:
        for row in result:
            name_id = row

            data = database.query(
                "delete from pgtarget_adduct where id  = %s", conn, [name_id])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }

    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash,
                "name": name,
                "identifiedBy": identifiedBy,
                "reason": "we did not find a name with the given properties"
            }, use_decimal=True)
        }


def delete_name(events, context):
    """

    :param events:
    :param context:
    :return:
    """

    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    name = urllib.parse.unquote(events['pathParameters']['name'])

    result = database.query(
        "select distinct pn.id from pgtarget p , pgtarget_name pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s",
        conn, [splash, library, name, identifiedBy])

    if result is not None:
        for row in result:
            name_id = row

            data = database.query(
                "delete from pgtarget_name where id  = %s", conn, [name_id])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }

    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash,
                "name": name,
                "identifiedBy": identifiedBy,
                "reason": "we did not find a name with the given properties"
            }, use_decimal=True)
        }


def make_name_primary(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            name = urllib.parse.unquote(events['pathParameters']['name'])

            result = database.query(
                "SELECT exists (SELECT 1 FROM pgtarget pt WHERE \"method_id\" = (%s) and \"splash\" = (%s) and dtype = 'PgInternalTarget' LIMIT 1)",
                conn, [method_name, splash])

            if result[0][0] == 0:
                return {
                    "statusCode": 404,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": ""
                }
            else:
                try:
                    database.query(
                        "update pgtarget pt set target_name = (%s) where  \"method_id\" = (%s) and \"splash\" = (%s) ",
                        conn, [name, method_name, splash])
                    # create a response
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "library": method_name,
                            "splash": splash
                        }, use_decimal=True)
                    }
                except Exception as e:
                    traceback.print_exc()
                    return {
                        "statusCode": 500,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "error": str(e),
                            "library": method_name
                        }, use_decimal=True)
                    }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name and a splash"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }


def register_name(events, context):
    """
    registers a new name for a given target
    :param events:
    :param context:
    :return:
    """
    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    name = urllib.parse.unquote(events['pathParameters']['name'])
    comment = events.get('body', "")

    logger.info(f"{splash} - {library} - {identifiedBy} - {name}")
    # load compound to get the correct id
    result = database.query(
        "select p.id as \"target_id\", pn.id as \"name_id\" from pgtarget p , pgtarget_name pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s",
        conn, [splash, library, name, identifiedBy])

    if result is None:
        result = database.query(
            "select p.id from pgtarget p where splash = (%s) and \"method_id\" = (%s)",
            conn, [splash, library])

        if result is not None and len(result) > 0:
            id = result[0][0]
        else:
            return {
                "statusCode": 404,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "library": library,
                    "splash": splash
                }, use_decimal=True)
            }
    elif len(result) > 0:
        id = result[0][0]

        for row in result:
            name_id = row[1]

            result = database.query(
                "delete from pgtarget_name where id = %s",
                conn, [name_id])

    # now register the given name and associated information
    # 1. get new sequence number
    result = database.query("select nextval('hibernate_sequence')", conn)

    newNameId = result[0][0]

    result = database.query(
        "insert into pgtarget_name(\"id\",\"name\",\"identified_by\",\"comment\",\"target_id\") values(%s,%s,%s,%s,%s)",
        conn, [newNameId, name, identifiedBy, comment, id])
    # create a response
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "members": True,
            "library": library,
            "splash": splash
        }, use_decimal=True)
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
                "SELECT count(*) FROM public.pg_internal_target_members a, pgtarget b where b.splash = (%s) and b.\"method_id\" = (%s)",
                conn, [splash, method_name])

            try:
                if result[0][0] > 0:  # target has members
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "members": True,
                            "count": result[0][0],
                            "library": method_name,
                            "splash": splash
                        }, use_decimal=True)
                    }
                else:  # target doesnt have members
                    return {
                        "statusCode": 200,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "members": False,
                            "count": result[0][0],
                            "library": method_name,
                            "splash": splash
                        }, use_decimal=True)
                    }
            except Exception as e:
                traceback.print_exc()
                return {
                    "statusCode": 500,
                    "headers": headers.__HTTP_HEADERS__,
                    "body": json.dumps({
                        "error": str(e),
                        "library": method_name
                    }, use_decimal=True)
                }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name and a splash"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
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
            # logger.info(f"loading all compounds for: {method_name} and splash {splash} limit {limit} and offset {offset}")
            transform = lambda x: x[0]
            sql = "SELECT members FROM public.pgtarget a, pg_internal_target_members b where a.id = b.pg_internal_target_id and  \"method_id\" = %s and splash = %s limit %s offset %s  "

            return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                params=[method_name, splash, limit, offset])
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name",

                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters",

            }, use_decimal=True)
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
            logger.info(f"loading all compounds for: {method_name} limit {limit} and offset {offset}")
            transform = lambda x: x[0]

            if 'type' in events['pathParameters']:

                target_type = events['pathParameters']['type']
                sql = "SELECT splash  FROM public.pgtarget where \"method_id\" = %s and target_type = %s and dtype = 'PgInternalTarget'  limit %s offset %s  "
                return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                    params=[method_name, target_type, limit, offset])
            else:
                sql = "SELECT splash  FROM public.pgtarget where \"method_id\" = %s and dtype = 'PgInternalTarget' limit %s offset %s  "
                return database.html_response_query(sql=sql, connection=conn, transform=transform,
                                                    params=[method_name, limit, offset])

        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name",

                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters",

            }, use_decimal=True)
        }


def get(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])

            def generate_metas_list(x):
                names = database.query(
                    "select pn.identified_by, pn.name, pn.value, pn.\"comment\" "
                    "from pgtarget p, pgtarget_meta pn "
                    "where p.id = pn.target_id and p.id = %s",
                    conn, [x])

                logger.info("received metadata: {}".format(names))
                if names is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'identifiedBy': y[0], 'name': y[1], 'value': y[2], 'comment': y[3]}, names))

            def generate_comments_list(x):
                names = database.query(
                    "select pn.identified_by, pn.\"comment\" "
                    "from pgtarget p, pgtarget_comment pn "
                    "where p.id = pn.target_id and p.id = %s",
                    conn, [x])

                logger.info("received comments: {}".format(names))
                if names is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'identifiedBy': y[0], 'comment': y[1]}, names))

            def generate_adducts_list(x):
                names = database.query(
                    "select pn.identified_by, pn.\"name\", pn.\"comment\" "
                    "from pgtarget p, pgtarget_adduct pn "
                    "where p.id = pn.target_id and p.id = %s",
                    conn, [x])

                logger.info("received adducts: {}".format(names))
                if names is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'name': y[1], 'identifiedBy': y[0], 'comment': y[2]}, names))

            def generate_name_list(x):
                names = database.query(
                    "select pn.identified_by, pn.\"name\", pn.\"comment\" "
                    "from pgtarget p, pgtarget_name pn "
                    "where p.id = pn.target_id and p.id = %s",
                    conn, [x])

                logger.info("received names: {}".format(names))
                if names is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'name': y[1], 'identifiedBy': y[0], 'comment': y[2]}, names))

            def generate_samples_list(splash, method):
                samples = database.query(
                    "select distinct file_name "
                    "from pgtarget p, pgtarget_samples ps, pgsample p2 "
                    "where p.id = ps.targets_id and p2.id = ps.samples_id and splash = %s and method_id = %s",
                    conn, [splash, method])

                logger.info("received samples: {}".format(samples))
                if samples is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'name': y[0]}, samples)
                    )

            def generate_status_list(splash):
                print(f"splash: {splash}")
                statuses = database.query(
                    "select distinct clean, identified_by "
                    "from pgspectrum_quality ps "
                    "where ps.target_id = %s",
                    conn, [splash])

                logger.info("received statuses: {}".format(statuses))
                if statuses is None:
                    return []
                else:
                    return list(
                        map(lambda y: {'clean': y[0], 'identifiedBy': y[1]}, statuses)
                    )

            transform = lambda x: {
                'id': x[0],
                'accurate_mass': x[1],
                'target_type': x[2],
                'inchi_key': x[3],
                'method': x[4],
                'ms_level': x[5],
                'required_for_correction': x[7],
                'retention_index': x[8],
                'spectrum': x[9],
                'splash': x[10],
                'preferred_name': x[11],
                'preferred_adduct': x[14],
                'associated_names': generate_name_list(x[0]),
                'associated_adducts': generate_adducts_list(x[0]),
                'associated_comments': generate_comments_list(x[0]),
                'associated_meta': generate_metas_list(x[0]),
                'associated_statuses': generate_status_list(x[0]),
                'unique_mass': x[12],
                'precursor_mass': x[13],
                'samples': generate_samples_list(x[10], x[4])
            }
            result = database.html_response_query(
                "SELECT id, accurate_mass, target_type, inchi_key, \"method_id\", ms_level, "
                "raw_spectrum, required_for_correction, retention_index, spectrum, splash, target_name, "
                "unique_mass, precursor_mass, adduct_name "
                "FROM pgtarget pt "
                "WHERE \"method_id\" = %s and \"splash\" = %s and dtype='PgInternalTarget'",
                conn, [method_name, splash], transform=transform)

            return result
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name and a splash"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }


def exists(events, context):
    if 'pathParameters' in events:
        if 'library' in events['pathParameters'] and 'splash' in events['pathParameters']:
            method_name = urllib.parse.unquote(events['pathParameters']['library'])
            splash = urllib.parse.unquote(events['pathParameters']['splash'])
            result = database.query(
                "SELECT exists (SELECT 1 FROM pgtarget pt WHERE \"method_id\" = (%s) and \"splash\" = (%s) and dtype = 'PgInternalTarget' LIMIT 1)",
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
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "exists": result[0][0],
                            "library": method_name,
                            "splash": splash
                        }, use_decimal=True)
                    }
                except Exception as e:
                    traceback.print_exc()
                    return {
                        "statusCode": 500,
                        "headers": headers.__HTTP_HEADERS__,
                        "body": json.dumps({
                            "error": str(e),
                            "library": method_name
                        }, use_decimal=True)
                    }
        else:
            return {
                "statusCode": 500,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "error": "you need to provide a 'library' name and a splash"
                }, use_decimal=True)
            }
    else:
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": "missing path parameters"
            }, use_decimal=True)
        }


def register_meta(events, context):
    """
    registers a new adduct for a given target
    :param events:
    :param context:
    :return:
    """
    splash = urllib.parse.unquote(events['pathParameters']['splash'])
    library = urllib.parse.unquote(events['pathParameters']['library'])
    identifiedBy = urllib.parse.unquote(events['pathParameters']['identifiedBy'])
    name = urllib.parse.unquote(events['pathParameters']['name'])
    value = urllib.parse.unquote(events['pathParameters']['value'])

    comment = events.get('body', '')

    logger.info(f"{splash} - {library} - {identifiedBy} - {name}")
    # load compound to get the correct id
    result = database.query(
        "select p.id, pn.id  from pgtarget p , pgtarget_meta pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s) and pn.\"name\"=%s and \"identified_by\" = %s and pn.\"value\" = %s",
        conn, [splash, library, name, identifiedBy, value])

    if result is None:
        result = database.query(
            "select p.id from pgtarget p where splash = (%s) and \"method_id\" = (%s)",
            conn, [splash, library])

        if result is not None and len(result) > 0:
            id = result[0][0]
        else:
            return {
                "statusCode": 404,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps({
                    "library": library,
                    "splash": splash
                }, use_decimal=True)
            }
    elif len(result) > 0:
        id = result[0][0]

        for row in result:
            name_id = row[1]
            result = database.query(
                "delete from pgtarget_meta  where id  = %s",
                conn, [name_id])

    # now register the given name and associated information
    # 1. get new sequence number
    result = database.query("select nextval('hibernate_sequence')", conn)

    newNameId = result[0][0]

    result = database.query(
        "insert into pgtarget_meta(\"id\",\"name\",\"value\",\"identified_by\",\"comment\",\"target_id\") values(%s,%s,%s,%s,%s,%s)",
        conn, [newNameId, name, value, identifiedBy, comment, id])
    # create a response
    return {
        "statusCode": 200,
        "headers": headers.__HTTP_HEADERS__,
        "body": json.dumps({
            "members": True,
            "library": library,
            "splash": splash
        }, use_decimal=True)
    }


def delete_meta(events, context):
    """
    TODO: REVISE ME - delete query has wrong arguments
    """
    splash = events['pathParameters']['splash']
    library = events['pathParameters']['library']

    result = database.query(
        "select DISTINCT p.id from pgtarget p , pgtarget_meta pn where p.id = pn.target_id and splash = (%s) and \"method_id\" = (%s)",
        conn, [splash, library])

    if result is not None:

        for row in result:
            name_id = row[0]

            database.query(
                "delete from pgtarget_meta where target_id  = %s",
                conn, [name_id])

        return {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }
    else:
        return {
            "statusCode": 404,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "library": library,
                "splash": splash
            }, use_decimal=True)
        }


def get_sorted(events, context):
    types_list = ['unconfirmed', 'is_member', 'consensus', 'confirmed']
    bool_map = {'true': True, 'false': False}
    directions = ['ASC', 'DESC']
    column_dict = {
        'tgt_id': 'id',
        'tgt_ri': 'retention_index',
        'pmz': 'precursor_mass',
        'name': 'target_name',
        'adduct': 'adduct_name'
    }
    query_params = {
        'limit': 10,
        'offset': 0,
        'order_by': column_dict['tgt_id'],
        'direction': 'ASC',
        'identified': False
    }
    rivalue = 0
    riaccuracy = 5
    pmzvalue = 0.0
    pmzaccuracy = 0.01

    if 'pathParameters' not in events:
        return {
            "statusCode": 400,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({"error": "missing path parameters"}, use_decimal=True)
        }

    if 'library' not in events['pathParameters']:
        return {
            "statusCode": 400,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({"error": "you need to provide a 'library' name"}, use_decimal=True)
        }
    else:
        query_params['method_name'] = urllib.parse.unquote(events['pathParameters']['library'])

    if 'tgt_type' not in events['pathParameters'] or events['pathParameters']['tgt_type'] not in types_list:
        query_params['tgt_type'] = 'CONFIRMED'
    else:
        query_params['tgt_type'] = urllib.parse.unquote(events['pathParameters']['tgt_type']).upper()

    try:
        if 'queryStringParameters' not in events or events['queryStringParameters'] is None:
            logger.info("WARN: using defaults")
        else:
            if 'limit' in events['queryStringParameters']:
                query_params['limit'] = int(events['queryStringParameters']['limit'])

            if 'offset' in events['queryStringParameters']:
                query_params['offset'] = int(events['queryStringParameters']['offset'])

            if 'order_by' in events['queryStringParameters'] and \
                    events['queryStringParameters']['order_by'].lower() in column_dict.keys():
                query_params['order_by'] = column_dict[events['queryStringParameters']['order_by'].lower()]

            if 'direction' in events['queryStringParameters'] and \
                    events['queryStringParameters']['direction'].upper() in directions:
                query_params['direction'] = events['queryStringParameters']['direction'].upper()

            if 'rivalue' in events['queryStringParameters']:
                rivalue = float(events['queryStringParameters']['rivalue'])
                if 'riaccuracy' in events['queryStringParameters']:
                    riaccuracy = float(events['queryStringParameters']['riaccuracy'])

            if 'pmzvalue' in events['queryStringParameters']:
                pmzvalue = float(events['queryStringParameters']['pmzvalue'])
                if 'pmzaccuracy' in events['queryStringParameters']:
                    pmzaccuracy = float(events['queryStringParameters']['pmzaccuracy'])

            if 'identified' in events['queryStringParameters']:
                if events['queryStringParameters']['identified'] in bool_map.keys():
                    query_params['identified'] = bool_map[events['queryStringParameters']['identified']]
                else:
                    raise Exception("Invalid value for queryString 'identified'. Please use 'true' or 'false'.")

            if 'name' in events['queryStringParameters']:
                query_params['tgt_name'] = urllib.parse.unquote(events['queryStringParameters']['name'])
                query_params['tgt_name_mask'] = f"%{query_params['tgt_name']}%"

        query_tables = "pgtarget t"
        query_filter = "WHERE t.method_id = %(method_name)s AND t.target_type = %(tgt_type)s " \
                       "AND t.dtype = 'PgInternalTarget'"
        query_order = f"ORDER BY t.{query_params['order_by']} {query_params['direction']}"
        query_limit = "LIMIT %(limit)s OFFSET %(offset)s"

        if 'tgt_name' in query_params:
            query_tables = "pgtarget t LEFT JOIN pgtarget_name tn ON t.id = tn.target_id"
            query_filter = f"{query_filter} AND tn.name ILIKE %(tgt_name_mask)s"
            if query_params['order_by'] not in events['queryStringParameters']:
                query_order = f"ORDER BY similarity(tn.name, %(tgt_name)s) DESC"
            else:
                query_order = f"ORDER BY similarity(tn.name, %(tgt_name)s) DESC, t.{query_params['order_by']} " \
                              f"{query_params['direction']}"

        if query_params['identified']:
            query_filter = f"{query_filter} AND position('unknown' in target_name) IN (0, null)"

        if rivalue > 0:
            query_filter = f"{query_filter} AND retention_index BETWEEN %(lower_ri)s AND %(upper_ri)s"
            query_params['lower_ri'] = rivalue - riaccuracy
            query_params['upper_ri'] = rivalue + riaccuracy

        if pmzvalue > 0:
            query_filter = f"{query_filter} AND precursor_mass BETWEEN %(lower_pmz)s AND %(upper_pmz)s"
            query_params['lower_pmz'] = pmzvalue - pmzaccuracy
            query_params['upper_pmz'] = pmzvalue + pmzaccuracy

        query = f"SELECT t.splash FROM {query_tables} {query_filter} {query_order} {query_limit}"

        transform = lambda x: x[0]
        result = database.html_response_query(query, conn, params=query_params, transform=transform)

        logger.info(f"Requested {query_params['limit']} results, returning {len(json.loads(result['body']))}")
        return result

    except Exception as ex:
        logger.error(ex)
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": str(ex)
            }, use_decimal=True)
        }

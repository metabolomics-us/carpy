import sys
import urllib.parse

import simplejson as json
from loguru import logger

from cis import database, headers

conn = database.connect()

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="compounds", level="INFO", backtrace=True,
           diagnose=True)

statusDic = {'true': True, 'false': False}

def get_status(events, context):
    """
    returns the status of a spectrum as clean: true or false
    :param events:
    :param context:
    :return:
    """

    if 'tgt_id' not in events['pathParameters']:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Missing path parameters 'tgt_id'"
            })
        }
    else:
        tgt_id = urllib.parse.unquote(events['pathParameters']['tgt_id'])

    if 'queryStringParameters' in events and events['queryStringParameters'] is not None \
            and 'identifiedBy' in events['queryStringParameters']:
        identified_by = urllib.parse.unquote(events['queryStringParameters']['identifiedBy'])
    else:
        identified_by = None

    try:
        # check if the user already marked this spectrum, possibly updating the 'clean' value
        query = "SELECT * FROM pgspectrum_quality " \
                "WHERE \"target_id\" = %s"
        params = [tgt_id]

        if identified_by is not None:
            query = query + " AND \"identified_by\" = %s"
            params = [tgt_id, identified_by]

        transform = lambda x: {
            "id": x[0],
            "clean": x[1],
            "target_id": x[2],
            "identifiedBy": x[3]
        }

        return database.html_response_query(query, conn, params, transform)
    except Exception as ex:
        logger.error(str(ex))
        response = {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": str(ex)
            }, use_decimal=True)
        }

    return response


def register_status(events, context):
    """
    registers a new clean or dirty flag for a given target's spectrum
    :param events:
    :param context:
    :return:
    """

    if 'tgt_id' not in events['pathParameters']:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Missing path parameters 'tgt_id'"
            })
        }
    else:
        tgt_id = urllib.parse.unquote(events['pathParameters']['tgt_id'])

    if 'queryStringParameters' not in events:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing parameters"
            })
        }
    else:
        if any([x not in events['queryStringParameters'] for x in ['clean', 'identifiedBy']]):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing parameters 'clean' or 'identifiedBy'"
                })
            }
    if events['queryStringParameters']['clean'] not in statusDic.keys():
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Invalid query parameter 'clean', must be 'true' or 'false'"
            })
        }

    clean = statusDic[events['queryStringParameters']['clean']]
    identified_by = urllib.parse.unquote(events['queryStringParameters']['identifiedBy'])

    try:
        # check if the user already marked this spectrum, possibly updating the 'clean' value
        query = "SELECT * FROM pgspectrum_quality " \
                "WHERE \"target_id\" = %s AND \"identified_by\" = %s"
        exists = database.query(query, conn, [tgt_id, identified_by])

        # now add the flag for the specified target
        if exists is None or len(exists) < 1:
            # 1. get new sequence number
            result = database.query("SELECT nextval('hibernate_sequence')", conn)
            new_status_id = result[0][0]
            # 2a. add record if user didn't mark this target
            query = "INSERT INTO pgspectrum_quality(\"clean\", \"id\", \"target_id\", \"identified_by\") " \
                    "VALUES (%s, %s, %s, %s)"
        else:
            # 2b. update record if user marked this target
            new_status_id = exists[0][0]
            query = "UPDATE pgspectrum_quality SET \"clean\" = %s " \
                    "WHERE \"id\" = %s AND \"target_id\" = %s AND \"identified_by\" = %s"

        database.query(query, conn, [clean, new_status_id, tgt_id, identified_by])

        # create a response
        response = {
            "statusCode": 200,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "target_id": tgt_id,
                "clean": clean
            }, use_decimal=True)
        }
    except Exception as ex:
        logger.error(str(ex))
        response = {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": str(ex)
            }, use_decimal=True)
        }

    return response


def delete_status(events, context):
    """
    deletes a clean or dirty flag for a given target's spectrum
    :param events:
    :param context:
    :return:
    """
    if 'tgt_id' not in events['pathParameters']:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Missing path parameters 'tgt_id'"
            })
        }
    else:
        tgt_id = urllib.parse.unquote(events['pathParameters']['tgt_id'])

    if 'queryStringParameters' not in events or 'identifiedBy' not in events['queryStringParameters']:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing query string parameter 'identifiedBy'"
            })
        }
    else:
        identified_by = events['queryStringParameters']['identifiedBy']

    try:
        result = database.query(
            "DELETE FROM pgspectrum_quality pc "
            "WHERE pc.\"target_id\" = %s AND pc.\"identified_by\" = %s",
            conn, [tgt_id, identified_by])

        response = {
            "statusCode": 204,
            "headers": headers.__HTTP_HEADERS__
        }
    except Exception as ex:
        logger.error(str(ex))
        response = {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": str(ex)
            }, use_decimal=True)
        }

    return response

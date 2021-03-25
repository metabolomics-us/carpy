import json
import os
import sys
import traceback
from typing import Optional, List

import psycopg2

from loguru import logger
from cis import headers

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="database", level="INFO", backtrace=True,
           diagnose=True)


def connect():
    """
    connects to the centrally configured database
    and returns a connection for us
    :return:
    """

    env = os.environ
    try:
        conn = psycopg2.connect(host=env['carrot_host'], database=env['carrot_database'],
                                user=env['carrot_username'], password=env['carrot_password'], port=env["carrot_port"])
        conn.set_session(readonly=False, autocommit=True)

        return conn
    except Exception as e:
        logger.error("ERROR: Unexpected error: Could not connect to database instance.")
        logger.error(e)


def query(sql: str, connection, params: Optional[List] = None) -> Optional[List]:
    """

    :param sql: your query string
    :param connection: your database connection
    :param params: optional positional parameters
    :return:
    """
    try:
        cur = connection.cursor()
        if params is None:
            cur.execute(sql)
        else:
            logger.warning(f'SQL: {sql}')
            cur.execute(sql, params)
        if cur.rowcount == 0 or cur.description is None:
            return None

        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(row)
        cur.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("observed exception: {}".format(error))
        raise error


def html_response_query(sql: str, connection, params: Optional[List] = None, transform: Optional = None,
                        return_404_on_empty=True) -> Optional[List]:
    """
    executes a query and converts the response to
    :param sql:
    :param connection:
    :param params:
    :return:
    """

    try:
        result = query(sql, connection, params)

        if result is None:
            result = []

        if len(result) == 0 and return_404_on_empty is True:
            return {
                "statusCode": 404,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps([])
            }
        else:
            if transform is not None:
                result = list(map(transform, result))
            return {
                "statusCode": 200,
                "headers": headers.__HTTP_HEADERS__,
                "body": json.dumps(
                    result
                )
            }
    except Exception as e:
        # traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": headers.__HTTP_HEADERS__,
            "body": json.dumps({
                "error": str(e),
            })
        }

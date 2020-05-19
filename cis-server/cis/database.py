import logging
import os
from typing import Optional, List

import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

        return conn
    except  Exception as e:
        logger.error("ERROR: Unexpected error: Could not connect to database instance.")
        logger.error(e)


def query(sql: str, connection) -> Optional[List]:
    try:
        cur = connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(row)
        cur.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("observed exception: {}".format(error))
        raise error

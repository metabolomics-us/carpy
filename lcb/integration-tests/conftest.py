import os

import pytest
from cisclient.client import CISClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from stasis_client.client import StasisClient

from lcb.node_evaluator import NodeEvaluator


@pytest.fixture
def database():
    import psycopg2
    con = psycopg2.connect(database="carrot-test", user="postgres", password="Fiehnlab2020",
                           host="lc-binbase-dev.czbqhgrlaqbf.us-west-2.rds.amazonaws.com", port="5432")
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    return con


@pytest.fixture
def drop_schema(database):

    # 2. drop database schema
    psqlCursor = database.cursor()
    try:
        psqlCursor.execute("drop schema public cascade")
    except:
        pass
    psqlCursor.execute("create schema public")
    psqlCursor.execute("ALTER SCHEMA public OWNER TO postgres")
    psqlCursor.close()

    return True

def pytest_generate_tests(metafunc):
    os.environ['CIS_URL'] = 'https://test-api.metabolomics.us/cis'
    os.environ['CIS_API_TOKEN'] = 'rDJfRW6ilG2WooOR72AaE3NqL4m23WvY6ub4FEoS'


@pytest.fixture()
def api_token():
    api_token = os.getenv('CIS_API_TOKEN', '')
    assert api_token is not '', "please ensure you are setting the CIS api token in your env under CIS_API_TOKEN!"

    return {'x-api-key': api_token.strip()}


@pytest.fixture
def cis_cli():
    return CISClient(os.getenv('CIS_URL'), os.getenv('CIS_API_TOKEN'))


@pytest.fixture()
def library_test_name():
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture
def stasis_token():
    token = "9MjbJRbAtj8spCJJVTPbP3YWc4wjlW0c7AP47Pmi"
    os.environ['STASIS_TOKEN'] = token
    return token


@pytest.fixture
def stasis_url():
    url = "https://test-api.metabolomics.us/stasis"
    os.environ['STASIS_URL'] = url
    return url


@pytest.fixture
def stasis_cli(stasis_token, stasis_url):
    return StasisClient(stasis_url, stasis_token)


@pytest.fixture
def node_evaluator(stasis_cli, cis_cli):
    return NodeEvaluator()

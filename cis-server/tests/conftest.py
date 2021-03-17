# Set AWS environment variables if they don't exist before importing moto/boto3
import json
import os

import moto
import pytest

os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'


@pytest.fixture
def requireMocking():
    """
    method which should be called before all other methods in tests. It basically configures our
    mocking context for stasis
    """

    lamb = moto.mock_lambda()
    lamb.start()

    os.environ["current_stage"] = "test"
    os.environ["carrot_database"] = "cis-test"
    os.environ["carrot_username"] = "postgres"
    os.environ["carrot_password"] = "Fiehnlab2020"
    os.environ["carrot_host"] = "lc-binbase-dev.czbqhgrlaqbf.us-west-2.rds.amazonaws.com"
    os.environ["carrot_port"] = "5432"

    yield
    lamb.stop()

    pass


@pytest.fixture()
def library_test_name() -> str:
    return "soqtof[M-H] | 6530a | c18 | negative"


@pytest.fixture()
def pos_library_test_name() -> str:
    return "soqe[M+H][M+NH4] | QExactive | test | positive"


@pytest.fixture()
def splash_test_name_with_members(pos_library_test_name, request):
    from cis import compounds
    result = request.config.cache.get("cis/members", None)

    if result is not None:
        print(f"using cached object: {result}")
        return result
    else:
        return __create_compound_with_member(compounds, pos_library_test_name)


def __create_compound_with_member(compounds, pos_library_test_name):
    db = compounds.database
    new_id = db.query("select nextval('hibernate_sequence')", compounds.conn)[0][0]
    new_member_id = new_id + 1
    splash_parent = "splash10-test-1000000000-00000000000000000001"
    splash_member = "splash10-test-2000000000-20000000000000000000"
    cur = compounds.conn.cursor()

    cur.execute('delete from pg_internal_target_members where members = %s', (splash_member, ))
    cur.execute('delete from pgtarget where splash in (%s,%s)', (splash_member, splash_parent))

    cur.execute('insert into pgtarget values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),'
                '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                ("PgInternalTarget", new_id, 341.66, None, None, "negative", 341.66,
                 "50.1:100 60.20:200", False,
                 583.787, "50.1:100 60.20:200", splash_parent, "test-parent-target", "UNCONFIRMED", 0,
                 "FIEHNLAB-809", "1f18173f91cb2b0e2fb2496d6855ad47ab5395ba", 2, 580.234, 10000.11, 860,
                 f"blank{pos_library_test_name}", pos_library_test_name,
                 "PgInternalTarget", new_member_id, 341.70, None, None, "negative", 341.70,
                 "50.2:100 60.21:210", False,
                 585.580, "50.2:100 60.21:210", splash_member,
                 "test-member-target",
                 "IS_MEMBER", 0, "FIEHNLAB-809", "1f18173f91cb2b0e2fb2496d6855ad47ab5395ba", 2, 582.234,
                 10000.11, 860, f"blank{pos_library_test_name}", pos_library_test_name))

    # add association
    cur.execute('insert into pg_internal_target_members values (%s, %s)', [new_id, splash_member])
    return splash_parent, pos_library_test_name


@pytest.fixture()
def splash_test_name_with_no_members(pos_library_test_name, request):
    from cis import compounds
    result = request.config.cache.get("cis/no_members", None)

    if result is not None:
        print(f"using cached object: {result}")
        return result
    else:
        print("loading all, takes forever and should be cached instead...")
        data = json.loads(
            compounds.all({'pathParameters': {'library': pos_library_test_name, 'limit': 10000}}, {})['body'])

    for num, splash in enumerate(data):
        response = compounds.get_members({'pathParameters': {'library': pos_library_test_name, 'splash': splash}}, {})
        if response['statusCode'] == 404:
            result = (data[num], pos_library_test_name)

            request.config.cache.set("cis/no_members", result)
            return result

    raise Exception(f"did not find a standard with no_members in {pos_library_test_name}")


@pytest.fixture()
def target_id():
    return '199'


@pytest.fixture()
def sample_name():
    return 'NIH_Lip_Std_CSH_POS_Brain_01'


@pytest.fixture()
def range_search():
    return 227.21, 0.01

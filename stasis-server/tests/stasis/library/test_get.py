import pytest
import simplejson as json

from stasis.library import get
from stasis.tables import TableManager


@pytest.fixture
def addData():
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item={
        'method': 'test_other | unknown | unknown | positive',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772163000
    })
    table.put_item(Item={
        'method': 'test_dynamo | unknown | unknown | unknown',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772263000
    })
    table.put_item(Item={
        'method': 'third | unknown | unknown | negative',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772363000
    })


def test_get(requireMocking, addData):
    # process data
    result = get.get({}, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])
    assert len(items) == 3
    assert all(x in items for x in ['test_other | unknown | unknown | positive',
                                    'test_dynamo | unknown | unknown | unknown',
                                    'third | unknown | unknown | negative'])

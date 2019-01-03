import pytest

from stasis.tables import TableManager
from stasis.target import delete


@pytest.fixture
def addData():
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib',
        'mz_rt': '12_1',
        'sample': 'tgtTest',
        'time': 1524772162698
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib',
        'mz_rt': '12.1_0.9',
        'sample': 'tgtTest2',
        'time': 1524772162698
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib',
        'mz_rt': '12_1',
        'sample': 'tgtTest2',
        'time': 1524772162800
    }))


def test_delete_success(requireMocking, addData):
    tm = TableManager()
    table = tm.get_target_table()
    count = table.item_count

    result = delete.delete({'pathParameters':
                                {'method': 'testLib',
                                 'mz_rt': '12_1'}
                            }, {})
    table.load()

    assert 204 == result['statusCode']
    assert table.item_count == (count - 1)


def test_delete_missing_method(requireMocking):
    result = delete.delete({'pathParameters':
                                {'method': '',
                                 'sample': 'tgtTest'}
                            }, {})
    assert 422 == result['statusCode']


def test_delete_missing_mz_rt(requireMocking):
    result = delete.delete({'pathParameters':
                                {'method': 'testLib'}
                            }, {})
    assert 422 == result['statusCode']


def test_delete_inexistent(requireMocking):
    result = delete.delete({'pathParameters':
                                {'method': 'test-del',
                                 'mz_rt': '999_9'}
                            }, {})
    assert 204 == result['statusCode']

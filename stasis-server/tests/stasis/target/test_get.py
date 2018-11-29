import pytest
import simplejson as json

from stasis.tables import TableManager
from stasis.target import get


@pytest.fixture
def addData():
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item={
        'method': 'testLib',
        'mz_rt': '12_1',
        'sample': 'tgtTest',
        'time': 1524772162698
    })
    table.put_item(Item={
        'method': 'testLib',
        'mz_rt': '12.1_0.9',
        'sample': 'tgtTest2',
        'time': 1524772162698
    })
    table.put_item(Item={
        'method': 'testLib',
        'mz_rt': '1_12',
        'sample': 'tgtTest2',
        'time': 1524772162800
    })
    table.put_item(Item={
        'method': 'test2Lib',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772163000
    })
    table.put_item(Item={
        'method': 'test_dynamo | unknown | unknown | unknown',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772163000
    })
    table.put_item(Item={
        'method': 'test_dynamo|unknown|unknown|unknown',
        'mz_rt': '2_15',
        'sample': 'tgtTest',
        'time': 1524772163000
    })


def test_get_with_mzrt(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib',
            "mz_rt": '12_1'
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0
    assert all('testLib' == x['method'] for x in items)


def test_get_without_mzrt(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib'
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0
    assert all('testLib' == x['method'] for x in items)


def test_get_method_with_spaces(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": "test_dynamo|unknown|unknown|unknown"
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0


def test_get_method_urlencoded(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": "test_dynamo%20%7c%20unknown%20%7c%20unknown%20%7c%20unknown"
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0

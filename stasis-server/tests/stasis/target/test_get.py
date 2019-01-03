import pytest
import simplejson as json

from stasis.tables import TableManager
from stasis.target import get


@pytest.fixture
def addData():
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib | unknown | unknown | unknown',
        'mz': 12,
        'rt': 1,
        'sample': 'tgtTest',
        'mz_rt': '12_1'
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib | unknown | unknown | unknown',
        'mz': 12.1,
        'rt': 0.9,
        'sample': 'tgtTest2',
        'mz_rt': '12.1_0.9'
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'testLib | unknown | unknown | unknown',
        'mz': 1,
        'rt': 12,
        'sample': 'tgtTest2',
        'mz_rt': '1_12'
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'test2Lib | unknown | unknown | unknown',
        'mz': 2,
        'rt': 15,
        'sample': 'tgtTest',
        'mz_rt': '2_15'
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'test_dynamo | unknown | unknown | unknown',
        'mz': 2,
        'rt': 15,
        'sample': 'tgtTest',
        'mz_rt': '2_15'
    }))
    table.put_item(Item=tm.sanitize_json_for_dynamo({
        'method': 'test_dynamo|unknown|unknown|unknown',
        'mz': 2,
        'rt': 15,
        'sample': 'tgtTest',
        'mz_rt': '2_15'
    }))


def test_get_with_mzrt(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib | unknown | unknown | unknown',
            "mz_rt": '12_1'
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0
    assert all('testLib | unknown | unknown | unknown' == x['method'] for x in items)


def test_get_without_mzrt(requireMocking, addData):
    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib | unknown | unknown | unknown'
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    items = json.loads(result['body'])['targets']
    assert len(items) > 0
    assert all('testLib | unknown | unknown | unknown' == x['method'] for x in items)


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

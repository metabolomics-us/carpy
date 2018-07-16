import simplejson as json

from stasis.tables import TableManager
from stasis.target import get


def test_get_with_mzrt(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item={
        'method': 'testLib',
        'mz_rt': '12_1',
        'sample': 'tgtTest',
        'time': 1524772162698
    })

    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib',
            "mz_rt": '12_1'
        }
    }, {})

    print('RESULT: %s' % result)

    assert 200 == result['statusCode']
    assert 'body' in result
    assert 'testLib' == json.loads(result['body'])['method']


def test_get_without_mzrt(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_target_table()
    table.put_item(Item={
        'method': 'testLib',
        'mz_rt': '12_1',
        'sample': 'tgtTest',
        'time': 1524772162698
    })

    # process data
    result = get.get({
        "pathParameters": {
            "method": 'testLib'
        }
    }, {})

    print('RESULT: %s' % result)

    assert 200 == result['statusCode']
    assert 'body' in result
    assert 'testLib' == json.loads(result['body'])['method']

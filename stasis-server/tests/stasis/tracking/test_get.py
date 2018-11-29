import pytest
import simplejson as json

from stasis.tables import TableManager
from stasis.tracking import get


def test_get(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_tracking_table()
    table.put_item(Item={
        "id": "test",
        "experiment": "unknown",
        "sample": "test",
        "status": [{"time": 1524772162698, "value": "processing"}]
    })

    # process data
    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    assert "test" == json.loads(result['body'])["id"]


def test_get_with_fileHandle(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_tracking_table()
    table.put_item(Item={
        "id": "test",
        "experiment": "unknown",
        "sample": "test",
        "status": [{"time": 1524772162698, "value": "PROCESSING", "fileHandle": "test.mzml"}]
    })

    # process data
    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
    assert 'test' == json.loads(result['body'])['id']
    assert 'test.mzml' == json.loads(result['body'])['status'][0]['fileHandle']


def test_get_inexistent_sample_returns_404(requireMocking):
    # query for inexistent sample
    result = get.get({
        "pathParameters": {
            "sample": "theIsNoSpoon"
        }
    }, {})

    assert 404 == result['statusCode']
    assert "sample not found" == json.loads(result['body'])['error']


@pytest.mark.parametrize('sample_count', [5, 10, 100, 1000, 10000])
def test_get_experiment(requireMocking, sample_count):
    tm = TableManager()
    table = tm.get_tracking_table()

    for x in range(0, sample_count):
        table.put_item(Item={
            "id": "test-{}".format(x),
            "experiment": "1",
            "sample": "test-{}".format(x),
            "status": [{"time": 1524772162698, "value": "PROCESSING", "fileHandle": "test.mzml"}]
        })

    result = get.get_experiment({
        'pathParameters': {
            'experiment': '1'
        }
    }, {})

    print(result
          )
    assert 200 == result['statusCode']
    assert sample_count == len(json.loads(result['body']))

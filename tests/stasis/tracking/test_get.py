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


def test_get_experiment(requireMocking):
    tm = TableManager()
    table = tm.get_tracking_table()
    table.put_item(Item={
        "id": "test",
        "experiment": "1",
        "sample": "test",
        "status": [{"time": 1524772162698, "value": "PROCESSING", "fileHandle": "test.mzml"}]
    })
    table.put_item(Item={
        "id": "test2",
        "experiment": "1",
        "sample": "test2",
        "status": [{"time": 1524772162698, "value": "PROCESSING", "fileHandle": "test2.mzml"}]
    })

    result = get.get_experiment({
        'pathParameters': {
            'experiment': '1'
        }
    }, {})

    assert 200 == result['statusCode']
    assert 2 == len(json.loads(result['body']))

import simplejson as json

from stasis.route.route import processTrackingMessage
from stasis.tracking import get


def test_get(requireMocking):
    # store data

    processTrackingMessage(json.loads(
        "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\"}]}"))
    # process data

    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 200
    assert 'body' in result
    assert json.loads(result['body'])["id"] == "test"


def test_get_with_fileHandle(requireMocking):
    # store data

    processTrackingMessage(json.loads(
        "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\", \"fileHandle\":\"test.mzml\"}]}"))
    # process data

    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 200
    assert 'body' in result
    assert json.loads(result['body'])["id"] == "test"
    assert json.loads(result['body'])["status"][0]["fileHandle"] == "test.mzml"


def test_get_inexistent_sample_returns_404(requireMocking):
    # query for inexistent sample
    result = get.get({
        "pathParameters": {
            "sample": "theIsNoSpoon"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 404
    assert json.loads(result['body'])['error'] == "sample not found"

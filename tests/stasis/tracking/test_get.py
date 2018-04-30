import json

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

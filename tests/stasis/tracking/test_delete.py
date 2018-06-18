import simplejson as json

from stasis.route.route import processTrackingMessage
from stasis.tracking import get, delete


def test_delete(requireMocking):
    # add test sample
    processTrackingMessage(json.loads(
        "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\"}]}"))

    # check it's there
    result = get.get({
        "pathParameters": {
            "sample": "test"
        }
    }, {})

    print("pre delete: %s" % result)
    assert json.loads(result['body'])["id"] == "test"

    # call deletion
    result = delete.delete({"delete": True, "pathParameters": {"sample": "test"}}, {})

    print("pos delete: %s" % result)
    # assert test data is gone
    assert result['statusCode'] == 204
    assert get.get({"pathParameters": {"sample": "test"}}, {})['statusCode'] == 404

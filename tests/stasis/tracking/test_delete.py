import simplejson as json

from stasis.route.route import processTrackingMessage
from stasis.tracking import get, delete


def test_delete(requireMocking):
    # add test sample
    processTrackingMessage(json.loads(
        "{\"id\": \"test-to-delete\", \"experiment\":\"unknown\", \"sample\": \"test-to-delete\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\"}]}"))

    # check it's there
    result = get.get({
        "pathParameters": {
            "sample": "test-to-delete"
        }
    }, {})

    print("pre delete: %s" % result)
    assert json.loads(result['body'])["id"] == "test-to-delete"

    # call deletion
    result = delete.delete({
        "pathParameters": {
            "sample": "test-to-delete"
        }
    }, {})

    print("pos delete: %s" % result)
    # assert test data is gone
    assert result['statusCode'] == 204
    assert get.get({"pathParameters": {"sample": "test-to-delete"}}, {})['statusCode'] == 404

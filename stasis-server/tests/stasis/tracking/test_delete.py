import simplejson as json

from stasis.tables import TableManager
from stasis.tracking import get, delete


def test_delete(requireMocking):
    # add test sample
    tm = TableManager()
    table = tm.get_tracking_table()
    table.put_item(Item={
        "id": "test-to-delete",
        "experiment": "unknown",
        "sample": "test-to-delete",
        "status": [
            {"time": 1524772162698, "value": "PROCESSING"}
        ]
    })

    # check it's there
    result = get.get({
        "pathParameters": {
            "sample": "test-to-delete"
        }
    }, {})

    assert json.loads(result['body'])["id"] == "test-to-delete"

    # call deletion
    result = delete.delete({
        "pathParameters": {
            "sample": "test-to-delete"
        }
    }, {})

    # assert test data is gone
    assert result['statusCode'] == 204
    assert get.get({"pathParameters": {"sample": "test-to-delete"}}, {})['statusCode'] == 404

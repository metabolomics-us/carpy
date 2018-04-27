import json

from stasis.tracking import get
from stasis.route.route import processTrackingMessage

import os
import boto3

dynamodb = boto3.resource('dynamodb')


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

    assert result['statusCode'] == 200
    assert 'body' in result
    assert json.loads(result['body'])["id"] == "test"
    assert json.loads(result['body'])["id"] == "test"

from unittest import TestCase

from moto import mock_lambda, sns

from stasis.route import route
from stasis.tracking import create

from moto import mock_sqs, mock_dynamodb, mock_dynamodb2, mock_sns
import boto3
import os

dynamodb = boto3.resource('dynamodb')


def test_route_tracking(requireMocking):
    # simulate a message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:tracking",
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"ENTERED\"}]}"
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'tracking'


def test_route_tracking_merge(requireMocking):
    # simulate a message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:tracking",
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"ENTERED\"}]}"
                }
            }]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'tracking'

    # add a second message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:tracking",
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\"}]}"
                }
            }]
    }, {})

    # validating that merge worked correctly
    table = dynamodb.Table(os.environ['trackingTable'])

    result = table.get_item(
        Key={
            'id': 'test'
        }
    )

    assert 'Item' in result
    assert len(result['Item']['status']) == 2


def test_route_metadata(requireMocking):
    # simulate a message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:metadata",
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"ENTERED\"}]}"
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'metadata'

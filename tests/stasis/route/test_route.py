from unittest import TestCase

from moto import mock_lambda, sns

from stasis.route import route
from stasis.tracking import create

from moto import mock_sqs, mock_dynamodb, mock_dynamodb2, mock_sns
import boto3
import os

from stasis.service.Persistence import Persistence


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

    # validating that merge worked correctly
    db = Persistence(os.environ['trackingTable'])

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

    result = db.load('test')
    assert len(result['status']) == 1

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

    result = db.load('test')
    assert len(result['status']) == 2


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

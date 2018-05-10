import json
import os

from stasis.route import route
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
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"ENTERED\",\"priority\":0}]}"
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
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, \"value\": \"PROCESSING\",\"priority\":300}]}"
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


def test_route_metadata_minix(requireMocking):
    # simulate a message

    message = {
        "url": "http://minix.fiehnlab.ucdavis.edu/rest/export/382171",
        "minix": True
    }
    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:metadata",
                    "Message": json.dumps(message)
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'metadata'


def test_route_result(requireMocking):
    # simulate a result message

    data = {
        "sample": "test",
        "time": 1525832496333,
        "correction": {
            "polynomial": 5,
            "sampleUsed": "test",
            "curve": [
                {"x": 121.12, "y": 121.2},
                {"x": 123.12, "y": 123.2}
            ]
        },
        "injections": {
            "test_1": {
                "results": [{
                    "target": {
                        "retentionIndex": 121.12,
                        "name": "test",
                        "id": "test_id",
                        "mass": 12.2},
                    "annotation": {
                        "retentionIndex": 121.2,
                        "intensity": 10.0,
                        "replaced": False,
                        "mass": 12.2}
                }, {
                    "target": {
                        "retentionIndex": 123.12,
                        "name": "test2",
                        "id": "test_id2",
                        "mass": 132.12},
                    "annotation": {
                        "retentionIndex": 123.2,
                        "intensity": 103.0,
                        "replaced": True,
                        "mass": 132.12}
                }]
            }
        }
    }

    # put some data
    route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:result",
                    "Message": json.dumps(data)
                }
            }
        ]
    }, {})

    reinj = {
        "sample": "test",
        "time": 1525832496333,
        "correction": {
            "polynomial": 5,
            "sampleUsed": "test",
            "curve": [
                {"x": 121.12, "y": 121.2},
                {"x": 123.12, "y": 123.2}
            ]
        }, "injections": {
            "test_2": {
                "results": [{
                    "target": {
                        "retentionIndex": 221.12,
                        "name": "test",
                        "id": "test_id",
                        "mass": 22.2},
                    "annotation": {
                        "retentionIndex": 221.2,
                        "intensity": 20.0,
                        "replaced": False,
                        "mass": 22.2}
                }, {
                    "target": {
                        "retentionIndex": 223.12,
                        "name": "test2",
                        "id": "test_id2",
                        "mass": 232.12},
                    "annotation": {
                        "retentionIndex": 223.2,
                        "intensity": 203.0,
                        "replaced": True,
                        "mass": 232.12
                    }
                }]
            }
        }
    }

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:result",
                    "Message": json.dumps(reinj)
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'result'

    injKeys = response[0]['body']['injections'].keys
    assert 'test_1' in injKeys
    assert 'test_2' in injKeys

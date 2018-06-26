import os

import simplejson as json

from stasis.route import route
from stasis.service.Bucket import Bucket


def test_route_tracking(requireMocking):
    # simulate a message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:tracking",
                    "Message": "{\"id\": \"test\", \"sample\": \"test\", \"status\": [{\"time\": 1524772162698, "
                               "\"value\": \"ENTERED\"}]} "
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'tracking'


def test_route_tracking_with_filehandle(requireMocking):
    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:tracking",
                    "Message": "{\"id\": \"test_filehandle\", \"experiment\": \"unknown\", \"sample\": "
                               "\"test_filehandle\", \"status\": [{\"time\": 1524772162698, \"value\": \"entered\", "
                               "\"fileHandle\":\"test_filehandle.mzml\"}]} "
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'tracking'


def test_route_metadata(requireMocking):
    # simulate a message

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:metadata",
                    "Message": "{\"id\": \"test\", \"experiment\": \"unknown\", \"sample\": \"test\", \"status\": [{"
                               "\"time\": 1524772162698, \"value\": \"ENTERED\"}]} "
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

    data = json.dumps({
        "id": "test",
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
                "results": [
                    {
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
                    }
                ]
            }
        }
    })

    # put some data
    route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:result",
                    "Message": data
                }
            }
        ]
    }, {})

    reinj = json.dumps({
        "id": "test",
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
    })

    response = route.route({
        "Records": [
            {
                "Sns": {
                    "Subject": "route:result",
                    "Message": reinj
                }
            }
        ]
    }, {})

    assert len(response) == 1
    assert response[0]['success']
    assert response[0]['event'] == 'result'

    db = Bucket(os.environ['resultTable'])

    result = json.loads(db.load('test'))

    injKeys = result['injections']
    assert 'test_1' in injKeys
    assert 'test_2' in injKeys

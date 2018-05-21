import time

import pytest
import simplejson as json

from stasis.tracking import create


def test_create_success(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': 'entered'})

    print(jsonString)
    response = create.create({'body': jsonString}, {})

    assert response["statusCode"], 200

    assert json.loads(response["body"])["status"][0]['value'], "ENTERED"

    assert json.loads(response["body"])["status"][0]['time'] >= timestamp


def test_create_with_fileHandle(requireMocking):
    timestamp = int(time.time() * 1000)

    jsonString = json.dumps({'sample': 'myTest', 'status': 'entered', 'fileHandle': 'myTest.d'})

    print(jsonString)
    response = create.create({'body': jsonString}, {})

    assert response["statusCode"], 200

    data = json.loads(response["body"])

    assert data["status"][0]['value'], "ENTERED"
    assert data["status"][0]['time'] >= timestamp
    assert data["status"][0]['fileHandle'] == "myTest.d"


def test_create_fail_invalid_status(requireMocking):
    with pytest.raises(Exception):
        create.create({'body': json.dumps({'sample': 'test', 'status': 'not a valid status'})}, {})

import sys

import simplejson as json
from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_compound", level="INFO", backtrace=True,
           diagnose=True)


def test_register_status(requireMocking, target_id, user_id):
    from cis import spectrum

    response = spectrum.register_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "clean": True,
            "identifiedBy": 'other' + user_id
        }
    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['clean']

    response = spectrum.register_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "clean": True,
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['clean']

    response = spectrum.register_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "clean": False,
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['clean'] is False


def test_register_status_no_clean(requireMocking, target_id, user_id):
    from cis import spectrum

    response = spectrum.register_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 400


def test_register_status_no_user(requireMocking, target_id):
    from cis import spectrum

    response = spectrum.register_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "clean": True
        }
    }, {})

    assert response['statusCode'] == 400


def test_register_status_no_target_id(requireMocking, user_id):
    from cis import spectrum

    response = spectrum.register_status({
        "pathParameters": {},
        "queryStringParameters": {
            "clean": True,
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 500


def test_delete_status(requireMocking, target_id, user_id):
    from cis import spectrum

    response = spectrum.delete_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "identifiedBy": 'other' + user_id
        }
    }, {})

    assert response['statusCode'] == 204


def test_get_status(requireMocking, target_id, user_id):
    from cis import spectrum

    response = spectrum.get_status({
        "pathParameters": {
            "tgt_id": target_id
        },
        "queryStringParameters": {
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])[0]['clean'] is False

    response = spectrum.get_status({
        "pathParameters": {
            "tgt_id": target_id + '2'
        },
        "queryStringParameters": {
            "identifiedBy": user_id
        }
    }, {})

    assert response['statusCode'] == 404
    assert len(json.loads(response['body'])) == 0

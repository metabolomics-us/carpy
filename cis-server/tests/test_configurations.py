import json
import sys

from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_cofiguration", level="INFO", backtrace=True,
           diagnose=True)


def test_profiles_without_params(requireMocking):
    from cis import configurations

    response = configurations.profiles({}, {})
    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing path parameters' in body['error']


def test_profiles_without_method(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {}}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing object type to query <target|sample>' in body['error']


def test_profiles_with_wrong_method(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'bad_wrong'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'invalid object type, it should be <target|sample>' in body['error']


def test_profiles_without_id(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'target'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing target_id' in body['error']


def test_target_profiles(requireMocking, target_id):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'target',
        'value': target_id
    }}, {})
    logger.info(response)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert len(body['profiles']) > 0


def test_sample_profiles(requireMocking, sample_name):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'sample',
        'value': sample_name
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert len(body['profiles']) > 0


def test_configs_without_params(requireMocking):
    from cis import configurations

    response = configurations.configs({}, {})
    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing path parameters' in body['error']


def test_configs_without_method(requireMocking):
    from cis import configurations

    response = configurations.configs({'pathParameters': {}}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing object type to query <target|sample>' in body['error']


def test_configs_with_wrong_method(requireMocking):
    from cis import configurations

    response = configurations.configs({'pathParameters': {
        'method': 'bad_wrong'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'invalid object type, it should be <target|sample>' in body['error']


def test_configs_without_id(requireMocking):
    from cis import configurations

    response = configurations.configs({'pathParameters': {
        'method': 'target'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing target_id' in body['error']


def test_target_config(requireMocking, target_id):
    from cis import configurations

    response = configurations.configs({'pathParameters': {
        'method': 'target',
        'value': target_id
    }}, {})
    logger.info(response)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert len(body['configs']) > 0


def test_sample_config(requireMocking, sample_name):
    from cis import configurations

    response = configurations.configs({'pathParameters': {
        'method': 'sample',
        'value': sample_name
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4))
    assert len(body) > 0

    assert len(body['configs']) > 0

import json
import os


def test_profiles_without_params(requireMocking):
    from cis import configurations

    print(os.environ)

    response = configurations.profiles({}, {})
    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing path parameters' in body['error']


def test_profiles_without_method(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {}}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing object type to query <target|sample>' in body['error']


def test_profiles_with_wrong_method(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'bad_wrong'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'invalid object type, it should be <target|sample>' in body['error']


def test_profiles_without_id(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'target'
    }}, {})

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0

    assert 'missing target_id' in body['error']


def test_target_profiles(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'target',
        'value': '361'
    }}, {})
    print(response)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0


def test_sample_profiles(requireMocking):
    from cis import configurations

    response = configurations.profiles({'pathParameters': {
        'method': 'sample',
        'value': 'test_sample'
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    print(json.dumps(body, indent=4))
    assert len(body) > 0

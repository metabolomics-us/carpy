import json


def test_libraries(requireMocking):
    from cis import libraries
    response = libraries.libraries({}, {})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    print(body)
    assert len(body) > 0


#def test_delete_library(requireMocking, library_test_name):
#    from cis import libraries
#    response = libraries.delete({'pathParameters': {
#        "library": library_test_name
#    }}, {})
#
#    assert response['statusCode'] == 200
#
#    response = libraries.exists({'pathParameters': {
#        "library": library_test_name
#    }}, {})
#
#    assert response['statusCode'] == 404
#    body = json.loads(response['body'])
#    assert body['exists'] is False


def test_exist_true(requireMocking, library_test_name):
    from cis import libraries
    response = libraries.exists({'pathParameters': {
        "library": library_test_name
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['exists']


def test_size(requireMocking, library_test_name):
    from cis import libraries
    response = libraries.size({'pathParameters': {
        "library": library_test_name
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    print(body)
    assert len(body) > 0

def test_exist_false(requireMocking, library_test_name):
    from cis import libraries
    response = libraries.exists({'pathParameters': {
        "library": library_test_name + "fasfdsfda"
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['exists'] is False

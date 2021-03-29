import json
import sys

from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_libraries", level="INFO", backtrace=True,
           diagnose=True)


def test_libraries(requireMocking):
    from cis import libraries
    response = libraries.libraries({}, {})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(json.dumps(body, indent=4, use_decimal=True))
    assert len(body) > 0


#def test_delete_library(requireMocking, library_test_name):
#   from cis import libraries
#   response = libraries.delete({'pathParameters': {
#       "library": library_test_name
#   }}, {})

#   assert response['statusCode'] == 200

#   response = libraries.exists({'pathParameters': {
#       "library": library_test_name
#   }}, {})

#   assert response['statusCode'] == 404
#   body = json.loads(response['body'])
#   assert body['exists'] is False


def test_exist_true(requireMocking, pos_library_test_name):
    from cis import libraries
    response = libraries.exists({'pathParameters': {
        "library": pos_library_test_name
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['exists']


def test_size(requireMocking, pos_library_test_name):
    from cis import libraries
    response = libraries.size({'pathParameters': {
        "library": pos_library_test_name
    }}, {})

    logger.info(response)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    logger.info(body)
    assert len(body) > 0


def test_exist_false(requireMocking, pos_library_test_name):
    from cis import libraries
    response = libraries.exists({'pathParameters': {
        "library": pos_library_test_name + "fasfdsfda"
    }}, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['exists'] is False

import json
import sys

from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_annotations", level="INFO", backtrace=False,
           diagnose=False)


def test_get_all(requireMocking, annotated_target):
    from cis import annotations

    response = annotations.get_all({
        "pathParameters": {
            "splash": annotated_target['splash']
        },
        "queryStringParameters": {
            "limit": 2,
            "offset": 0
        }
    }, {})
    logger.info(response)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    assert len(body['annotations']) == 2
    assert body['total_count'] == annotated_target['count']

    response = annotations.get_all({
        "pathParameters": {
            "splash": annotated_target['splash']
        },
        "queryStringParameters": {
            "limit": 2,
            "offset": 2
        }
    }, {})
    logger.info(response)
    body = json.loads(response['body'])

    assert len(body['annotations']) == 1

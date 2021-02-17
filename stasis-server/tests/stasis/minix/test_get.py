from stasis.minix import get


def test_get(requireMocking):
    # process data
    result = get.get({
        "pathParameters": {
            "id": 586898
        }
    }, {})

    assert 200 == result['statusCode']
    assert 'body' in result
import json

from pytest import fail


def test_getall(requireMocking, library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": library_test_name,
        "offset": 0,
        "limit": 10
    }

    }, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 10

    response = compounds.all({'pathParameters': {
        "library": library_test_name,
        "offset": 10,
        "limit": 5
    }

    }, {})

    body = json.loads(response['body'])
    assert len(body) == 5


def test_get_specific_compound(requireMocking, splash_test_name):
    from cis import compounds

    response = compounds.get({'pathParameters': {
        "library": splash_test_name[1],
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    assert result['method'] == splash_test_name[1]
    assert result['splash'] == splash_test_name[0]


def test_exist_specific_compound(requireMocking, splash_test_name):
    from cis import compounds

    response = compounds.exists({'pathParameters': {
        "library": splash_test_name[1],
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['exists'] == True
    assert json.loads(response['body'])['library'] == splash_test_name[1]
    assert json.loads(response['body'])['splash'] == splash_test_name[0]


def test_edit_specific_compound(requireMocking, library_test_name):
    fail()

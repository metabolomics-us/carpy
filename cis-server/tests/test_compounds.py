import json

from pytest import fail


def test_getall_by_type_unconfirmed(requireMocking, library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": library_test_name,
        "offset": 0,
        "limit": 10,
        "type": 'UNCONFIRMED'
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


def test_getall_by_type_unconfirmed_consensus(requireMocking, library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": library_test_name,
        "offset": 0,
        "limit": 10,
        "type": 'UNCONFIRMED_CONSENSUS'
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


def test_get_specific_compound_doesnt_exist(requireMocking, splash_test_name):
    from cis import compounds

    response = compounds.get({'pathParameters': {
        "library": "{}_not_real".format(splash_test_name[1]),
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 404


def test_exist_specific_compound_false(requireMocking, splash_test_name):
    from cis import compounds

    response = compounds.exists({'pathParameters': {
        "library": "{}_not real".format(splash_test_name[1]),
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 404


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


def test_compound_has_members(requireMocking, splash_test_name):
    """
    tests if a compound has more than 1 member
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.has_members({'pathParameters': {
        "library": splash_test_name[1],
        "splash": splash_test_name[0]
    }

    }, {})
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['members'] == True
    assert json.loads(response['body'])['library'] == splash_test_name[1]
    assert json.loads(response['body'])['splash'] == splash_test_name[0]
    assert json.loads(response['body'])['count'] > 0


def test_compound_get_members(requireMocking, splash_test_name):
    """
    tests if pagination works to load all members or a compound
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.get_members(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": splash_test_name[0]
        }

        }, {}

    )
    assert response['statusCode'] == 200
    assert len(json.loads(response['body'])) > 0


def test_compound_get_members_none(requireMocking, splash_test_name):
    """
    tests if pagination works to load all members or a compound
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.get_members(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}_none".format(splash_test_name[0])
        }

        }, {}

    )
    assert response['statusCode'] == 404


def test_edit_specific_compound(requireMocking, library_test_name):
    fail()


def test_compound_register_name(requireMocking, splash_test_name):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}".format(splash_test_name[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}".format(splash_test_name[0]),
            "identifiedBy": "test",
            "name": "test1"
        }

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name[1],
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 1
    assert result['associated_names'][0]['name'] == 'test1'
    assert result['associated_names'][0]['identifiedBy'] == 'test'
    assert result['associated_names'][0]['comment'] == ''


def test_compound_register_names(requireMocking, splash_test_name):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}".format(splash_test_name[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}".format(splash_test_name[0]),
            "identifiedBy": "test",
            "name": "test1"
        }

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name[1],
            "splash": "{}".format(splash_test_name[0]),
            "identifiedBy": "testA",
            "name": "test2"
        }

        }, {}

    )

    assert response['statusCode'] == 200

    response = compounds.get({'pathParameters': {
        "library": splash_test_name[1],
        "splash": splash_test_name[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 2

    assert result['associated_names'][0]['name'] == 'test1'
    assert result['associated_names'][0]['identifiedBy'] == 'test'
    assert result['associated_names'][0]['comment'] == ''

    assert result['associated_names'][1]['name'] == 'test2'
    assert result['associated_names'][1]['identifiedBy'] == 'testA'
    assert result['associated_names'][1]['comment'] == ''

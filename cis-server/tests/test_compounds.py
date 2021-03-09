import json
import random
import string

from pytest import fail


def test_getall_full_pagination(requireMocking, library_test_name):
    from cis import compounds

    more = True
    data = []
    while more:
        temp = json.loads(
            compounds.all({'pathParameters': {
                "library": library_test_name,
                "offset": len(data),
                "limit": 10,
            }

            }, {})['body']
        )

        more = len(temp) > 0
        for x in temp:
            data.append(x)

        print(len(data))
    print(len(data))
    assert len(data) > 10


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
    assert len(body) > 0

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


def test_get_specific_compound(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]

    print(json.dumps(result, indent=4))
    assert result['method'] == splash_test_name_with_no_members[1]
    assert result['splash'] == splash_test_name_with_no_members[0]


def test_get_specific_compound_doesnt_exist(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    response = compounds.get({'pathParameters': {
        "library": "{}_not_real".format(splash_test_name_with_no_members[1]),
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 404


def test_exist_specific_compound_false(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    response = compounds.exists({'pathParameters': {
        "library": "{}_not real".format(splash_test_name_with_no_members[1]),
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 404


def test_exist_specific_compound(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    response = compounds.exists({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    assert json.loads(response['body'])['exists'] == True
    assert json.loads(response['body'])['library'] == splash_test_name_with_no_members[1]
    assert json.loads(response['body'])['splash'] == splash_test_name_with_no_members[0]


def test_compound_has_members(requireMocking, splash_test_name_with_members):
    """
    tests if a compound has more than 1 member
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.has_members({'pathParameters': {
        "library": splash_test_name_with_members[1],
        "splash": splash_test_name_with_members[0]
    }

    }, {})
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['members'] == True
    assert json.loads(response['body'])['library'] == splash_test_name_with_members[1]
    assert json.loads(response['body'])['splash'] == splash_test_name_with_members[0]
    assert json.loads(response['body'])['count'] > 0


def test_compound_get_members(requireMocking, splash_test_name_with_members):
    """
    tests if pagination works to load all members or a compound
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.get_members(
        {'pathParameters': {
            "library": splash_test_name_with_members[1],
            "splash": splash_test_name_with_members[0]
        }

        }, {}

    )
    assert response['statusCode'] == 200
    assert len(json.loads(response['body'])) > 0


def test_compound_get_members_none(requireMocking, splash_test_name_with_members):
    """
    tests if pagination works to load all members or a compound
    :param requireMocking:
    :param splash_test_name:
    :return:
    """
    from cis import compounds
    response = compounds.get_members(
        {'pathParameters': {
            "library": splash_test_name_with_members[1],
            "splash": "{}_none".format(splash_test_name_with_members[0])
        }

        }, {}

    )
    assert response['statusCode'] == 404


def test_edit_specific_compound(requireMocking, library_test_name):
    fail('Not implemented')


def test_compound_no_registered_names(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200


def test_compound_register_comment(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    comments = ''.join(random.choice(string.ascii_lowercase) for x in range(1000))

    compounds.delete_comments(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }
        }, {}

    )

    response = compounds.register_comment(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test"
        },
            'body': comments

        }, {}
    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(json.dumps(result, indent=4))

    # the target might have more than 1 comment
    assert len(result['associated_comments']) > 0
    # check the values for the last created comments
    assert result['associated_comments'][-1]['identifiedBy'] == 'test'
    assert result['associated_comments'][-1]['comment'] == comments


def test_compound_register_adduct(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_adducts(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_adduct(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "Na+"
        }

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(json.dumps(result, indent=4))

    assert len(result['associated_adducts']) > 0
    assert result['associated_adducts'][-1]['name'] == 'Na+'
    assert result['associated_adducts'][-1]['identifiedBy'] == 'test'
    assert result['associated_adducts'][-1]['comment'] == ''

    response = compounds.delete_adducts(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "Na+"
        }

        }, {}
    )


def test_compound_register_adduct_with_comment(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_adducts(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_adduct(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "Na+"
        },
            'body': "gaga"

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(json.dumps(result, indent=4))

    assert len(result['associated_adducts']) > 0
    assert result['associated_adducts'][-1]['name'] == 'Na+'
    assert result['associated_adducts'][-1]['identifiedBy'] == 'test'
    assert result['associated_adducts'][-1]['comment'] == 'gaga'

    response = compounds.register_adduct(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test2",
            "name": "Na+2"
        },
            'body': "gaga"

        }, {}

    )
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    result = json.loads(response['body'])[0]
    pre_count = len(result['associated_adducts'])
    assert pre_count > 0

    response = compounds.delete_adduct(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test2",
            "name": "Na+2"
        },
            'body': "gaga"

        }, {}

    )
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    result = json.loads(response['body'])[0]
    assert len(result['associated_adducts']) == pre_count - 1


def test_compound_delete_name(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        },

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 1
    assert result['associated_names'][0]['name'] == 'test1'
    assert result['associated_names'][0]['identifiedBy'] == 'test'
    assert result['associated_names'][0]['comment'] == ''

    response = compounds.delete_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        },

        }, {}

    )

    print(response)
    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 0


def test_compound_register_name(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        },

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 1
    assert result['associated_names'][0]['name'] == 'test1'
    assert result['associated_names'][0]['identifiedBy'] == 'test'
    assert result['associated_names'][0]['comment'] == ''


def test_compound_register_name_with_comment(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        },
            'body': 'blah blah',
        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 1
    assert result['associated_names'][0]['name'] == 'test1'
    assert result['associated_names'][0]['identifiedBy'] == 'test'
    assert result['associated_names'][0]['comment'] == 'blah blah'

    compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test2",
            "name": "test2"
        },
            'body': 'blah blah',
        }, {}

    )

    response = compounds.delete_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        },
            'body': 'blah blah',
        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(result)

    assert len(result['associated_names']) == 1
    assert result['associated_names'][0]['name'] == 'test2'
    assert result['associated_names'][0]['identifiedBy'] == 'test2'
    assert result['associated_names'][0]['comment'] == 'blah blah'


def test_compound_register_names(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_names(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "test1"
        }

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.register_name(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "testA",
            "name": "test2"
        }

        }, {}

    )

    assert response['statusCode'] == 200

    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
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


def test_compound_register_meta(requireMocking, splash_test_name_with_no_members):
    from cis import compounds

    compounds.delete_meta(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
        }

        }, {}

    )

    response = compounds.register_meta(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "CID",
            "value": "1"
        }

        }, {}

    )

    response = compounds.register_meta(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "KEGG",
            "value": "C0002"
        }

        }, {}

    )
    response = compounds.register_meta(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "KEGG",
            "value": "C0002"
        }

        }, {}

    )

    response = compounds.register_meta(
        {'pathParameters': {
            "library": splash_test_name_with_no_members[1],
            "splash": "{}".format(splash_test_name_with_no_members[0]),
            "identifiedBy": "test",
            "name": "KEGG",
            "value": "C0001"
        }

        }, {}

    )

    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    print(json.dumps(result, indent=4))

    assert len(result['associated_meta']) == 3

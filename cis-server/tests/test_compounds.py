import json
import random
import string
import sys
import urllib.parse

from pytest import fail
from loguru import logger

# initialize the loguru logger
logger.add(sys.stdout, format="{time} {level} {message}", filter="test_compound", level="INFO", backtrace=True,
           diagnose=True)


def test_getall_full_pagination(requireMocking, pos_library_test_name):
    from cis import compounds

    more = True
    data = []
    while more:
        temp = json.loads(
            compounds.all({'pathParameters': {
                "library": pos_library_test_name,
                "offset": len(data),
                "limit": 10,
            }

            }, {})['body']
        )

        more = len(temp) > 0
        for x in temp:
            data.append(x)

        logger.info(len(data))
    logger.info(len(data))
    assert len(data) > 10


def test_getall_by_type_is_member(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
        "offset": 0,
        "limit": 10,
        "type": 'IS_MEMBER'
    }

    }, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) > 0

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
        "offset": 10,
        "limit": 5
    }

    }, {})

    body = json.loads(response['body'])
    assert len(body) == 5


def test_getall_by_type_unconfirmed_consensus(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
        "offset": 0,
        "limit": 10,
        "type": 'UNCONFIRMED_CONSENSUS'
    }

    }, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 10

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
        "offset": 10,
        "limit": 5
    }

    }, {})

    body = json.loads(response['body'])
    assert len(body) == 5


def test_getall(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
        "offset": 0,
        "limit": 10
    }

    }, {})

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 10

    response = compounds.all({'pathParameters': {
        "library": pos_library_test_name,
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

    logger.info(json.dumps(result, indent=4))
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


def test_edit_specific_compound(requireMocking, pos_library_test_name):
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
    logger.info(json.dumps(result, indent=4))

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
    logger.info(json.dumps(result, indent=4))

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
    logger.info(json.dumps(result, indent=4))

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
    logger.info(result)

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

    logger.info(response)
    assert response['statusCode'] == 200
    response = compounds.get({'pathParameters': {
        "library": splash_test_name_with_no_members[1],
        "splash": splash_test_name_with_no_members[0]
    }

    }, {})

    assert response['statusCode'] == 200
    result = json.loads(response['body'])[0]
    logger.info(result)

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
    logger.info(result)

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
    logger.info(result)

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
    logger.info(result)

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
    logger.info(result)

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
    logger.info(json.dumps(result, indent=4))

    assert len(result['associated_meta']) == 3


def test_get_sorted_defaults(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'queryStringParameters': {
            'limit': 10,
            'offset': 0,
            'order_by': 'ri',
            'direction': 'asc'
        }
    }, {})

    assert response['statusCode'] == 200

    compounds = json.loads(response['body'])
    assert len(compounds) == 10


def test_get_sorted_queryString_none(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'path': 'something to shut-up pytest\'s KeyError',
        'multiValueQueryStringParameters': 'something to shut-up pytest\'s KeyError',
        'queryStringParameters': None
    }, {})

    logger.info(response)

    assert response['statusCode'] == 200
    compounds = json.loads(response['body'])
    assert len(compounds) == 10


def test_get_sorted_big_page(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'queryStringParameters': {'limit': '100'}
    }, {})

    assert response['statusCode'] == 200

    compounds = json.loads(response['body'])
    assert len(compounds) == 100


def test_get_sorted_wrong_path(requireMocking, library_test_name):
    from cis import compounds

    response = compounds.get_sorted({}, {})

    assert response['statusCode'] == 400
    assert json.loads(response['body'])['error'] == 'missing path parameters'


def test_get_sorted_no_library(requireMocking, library_test_name):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {},
        'queryStringParameters': {'limit': 10}
    }, {})

    assert response['statusCode'] == 400
    assert json.loads(response['body'])['error'] == "you need to provide a 'library' name"


def test_get_sorted_alt_type(requireMocking, splash_test_name_with_members):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {'library': splash_test_name_with_members[1]},
        'queryStringParameters': {'limit': 10}
    }, {})

    assert response['statusCode'] == 200

    splashes = compounds.get_members({
        'pathParameters': {'library': splash_test_name_with_members[1],
                           'splash': splash_test_name_with_members[0]}
    }, {})['body']

    types = [json.loads(compounds.get({'pathParameters': {'library': splash_test_name_with_members[1],
                                                          'splash': s}}, {})['body'])[0]['target_type'] for s in
             json.loads(splashes)]

    assert list(dict.fromkeys(types))[0] == 'IS_MEMBER'


def test_get_sorted_second_page(requireMocking, pos_library_test_name):
    from cis import compounds

    first = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'offset': 0}
    }, {})

    second = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'offset': 10}
    }, {})

    assert first['statusCode'] == 200
    assert second['statusCode'] == 200

    assert json.loads(first['body']) != json.loads(second['body'])


def test_get_sorted_compare_sorts(requireMocking, pos_library_test_name):
    from cis import compounds

    cid = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'order_by': 'tgt_id'}
    }, {})

    ri = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'order_by': 'tgt_ri'}
    }, {})

    pmz = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'order_by': 'pmz'}
    }, {})

    name = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'order_by': 'name'}
    }, {})

    adduct = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {'limit': 10, 'order_by': 'adduct'}
    }, {})

    assert cid['statusCode'] == 200
    assert ri['statusCode'] == 200
    assert pmz['statusCode'] == 200
    assert name['statusCode'] == 200
    assert adduct['statusCode'] == 200


def test_get_sorted_with_range(requireMocking, pos_library_test_name, range_search):
    from cis import compounds

    splashes = compounds.get_sorted({
        'pathParameters': {'library': urllib.parse.quote(pos_library_test_name)},
        'queryStringParameters': {
            'limit': 10,
            'order_by': 'pmz',
            'value': range_search[0],
            'accuracy': range_search[1]
        }
    }, {})

    assert splashes['statusCode'] == 200
    comps_obj = [json.loads(compounds.get({
        'pathParameters': {'library': pos_library_test_name,
                           'splash': c}
    }, {})['body'])[0] for c in json.loads(splashes['body'])]
    assert len(comps_obj) > 0

    assert comps_obj[0]['precursor_mass'] >= range_search[0] - range_search[1]
    assert comps_obj[-1]['precursor_mass'] <= range_search[0] + range_search[1]
    assert [comps_obj[x]['precursor_mass'] < comps_obj[x + 1]['precursor_mass'] for x in range(0, len(comps_obj) - 1)]
    assert comps_obj[0]['precursor_mass'] - comps_obj[-1]['precursor_mass'] < 0


def test_get_ranges_gibberish(requireMocking, pos_library_test_name):
    from cis import compounds

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'path': 'something to shut-up pytest\'s KeyError',
        'multiValueQueryStringParameters': 'something to shut-up pytest\'s KeyError',
        'queryStringParameters': {
            'value': 'boom'
        }
    }, {})

    assert response['statusCode'] == 500

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'path': 'something to shut-up pytest\'s KeyError',
        'multiValueQueryStringParameters': 'something to shut-up pytest\'s KeyError',
        'queryStringParameters': {
            'value': 199,
            'accuracy': 1
        }
    }, {})

    assert response['statusCode'] == 200

    response = compounds.get_sorted({
        'pathParameters': {
            'library': urllib.parse.quote(pos_library_test_name)
        },
        'path': 'something to shut-up pytest\'s KeyError',
        'multiValueQueryStringParameters': 'something to shut-up pytest\'s KeyError',
        'queryStringParameters': {
            'value': 200,
            'accuracy': 'hacked'
        }
    }, {})

    assert response['statusCode'] == 500

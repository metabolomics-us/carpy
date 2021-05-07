from pprint import pprint

import simplejson as json

from similarity import similarity


def test_list_algorithms():
    algos = similarity.list_algorithms()
    pprint(json.loads(algos['body']))
    assert(algos['statusCode'] == 200)


def test_all_similarities(require_mocking, spectrum_pair):
    result = similarity.all_similarities({
        "queryStringParameters": {
            "unknown": spectrum_pair['unknown'],
            "reference": spectrum_pair['reference']
        }
    }, {})

    pprint(result)
    assert(result['statusCode'] == 200)


def test_similarity(require_mocking, spectrum_pair):
    result = similarity.all_similarities({
        "pathParameters": {
            "algorithm": "entropy"
        },
        "queryStringParameters": {
            "unknown": spectrum_pair['unknown'],
            "reference": spectrum_pair['reference']
        }
    }, {})

    pprint(result)
    assert(result['statusCode'] == 200)

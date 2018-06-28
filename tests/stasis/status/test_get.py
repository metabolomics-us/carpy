import simplejson as json

from stasis.status import get


def test_get_status_map(requireMocking):
    states = {
        'entered': 1,
        'acquired': 100,
        'converted': 200,
        'processing': 300,
        'deconvoluted': 310,
        'corrected': 320,
        'annotated': 330,
        'quantified': 340,
        'replaced': 350,
        'exported': 400,
        'failed': 666
    }

    result = get.get({}, {})

    status = json.loads(result['body'])

    assert status == states

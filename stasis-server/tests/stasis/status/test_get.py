import simplejson as json

from stasis.status import get


def test_get_status_map(requireMocking):
    states = {
        'entered': 1,
        'acquired': 100,
        'converted': 200,
        'scheduled': 300,
        'processing': 400,
        'deconvoluted': 410,
        'corrected': 420,
        'annotated': 430,
        'quantified': 440,
        'replaced': 450,
        'exported': 500,
        'finished': 600,
        'failed': 900
    }

    result = get.get({}, {})

    status = json.loads(result['body'])

    assert status == states

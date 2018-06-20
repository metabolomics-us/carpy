import time

import simplejson as json

from stasis.acquisition import create
from stasis.util.minix_parser import parse_minix_xml


def test_create_success_gctof(requireMocking):
    data = parse_minix_xml("http://minix.fiehnlab.ucdavis.edu/rest/export/63618")

    timestamp = int(time.time() * 1000)

    for x in data:
        print(x)
        jsonString = json.dumps(x)

        response = create.create({'body': jsonString}, {})

        assert response["statusCode"], 200
        assert json.loads(response["body"])["acquisition"]['instrument'] == "Leco GC-Tof"
        assert json.loads(response["body"])["acquisition"]['name'] == "Leco GC-Tof"
        assert json.loads(response["body"])["acquisition"]['ionisation'] == "positive"
        assert json.loads(response["body"])["acquisition"]['method'] == "gcms"
        assert json.loads(response["body"])["metadata"]['species'] == "Medicago sativa"
        assert json.loads(response["body"])["metadata"]['organ'] == "aerial part"


def test_create_success_minix(requireMocking):
    data = {
        "id": 63618
    }
    response = create.fromMinix({'body': json.dumps(data)}, {})

    assert json.loads(response["body"])['id'] == 63618
    assert 'body' in response


def test_create_non_minix(requireMocking):
    data = {
        'sample': 'test_no_minix',
        'experiment': '1',
        'acquisition': {
            'instrument': 'test inst',
            'name': 'method blah',
            'ionisation': 'positive',  # psotivie || negative
            'method': 'gcms'  # gcms || lcms
        },
        'processing': {
            'method': 'gcms'
        },
        'metadata': {
            'class': '12345',
            'species': 'alien',
            'organ': 'honker'
        },
        'userdata': {
            'label': 'filexxx',
            'comment': '',
        },
    }

    response = create.create({'body': json.dumps(data)}, {})

    assert response['statusCode'] == 200
    assert 'body' in response
    assert json.loads(response['body'])['id'] == 'test_no_minix'

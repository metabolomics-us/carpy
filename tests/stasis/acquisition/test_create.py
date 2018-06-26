import simplejson as json

from stasis.acquisition import create
from stasis.util.minix_parser import parse_minix_xml


def test_create_success_gctof(requireMocking):
    data = parse_minix_xml("http://minix.fiehnlab.ucdavis.edu/rest/export/63618")

    for x in data:
        jsonString = json.dumps(x)

        response = create.create({'body': jsonString}, {})

        assert 200 == response['ResponseMetadata']['HTTPStatusCode']
        assert "Leco GC-Tof" == response['Attributes']["acquisition"]['instrument']
        assert "GCTOF" == response['Attributes']["acquisition"]['name']
        assert "positive" == response['Attributes']["acquisition"]['ionisation']
        assert "gcms" == response['Attributes']["acquisition"]['method']
        assert "Medicago sativa" == response['Attributes']["metadata"]['species']
        assert "aerial part" == response['Attributes']["metadata"]['organ']


def test_create_success_minix(requireMocking):
    data = {"id": 63618}
    response = create.fromMinix({'body': json.dumps(data)}, {})

    assert 0 < len(response)

    for item in response:
        assert 200 == item['ResponseMetadata']['HTTPStatusCode']
        assert '63618' == item['Attributes']['experiment']
        assert item['Attributes']['id'] == item['Attributes']['sample']


def test_create_non_minix(requireMocking):
    data = {
        'sample': 'test_no_minix',
        'experiment': '1',
        'acquisition': {
            'instrument': 'test inst',
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

    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert 'Attributes' in response
    assert response['Attributes']['id'] == 'test_no_minix'

import simplejson as json
from moto import mock_s3

from stasis.acquisition import create
from stasis.tracking import get
from stasis.util.minix_parser import parse_minix_xml


@mock_s3
def test_create_success_gctof(requireMocking):
    data = parse_minix_xml("http://minix.fiehnlab.ucdavis.edu/rest/export/63618")

    for x in data:
        jsonString = json.dumps(x)

        response = create.create({'body': jsonString}, {})

        assert 'isBase64Encoded' in response
        assert 200 == response['statusCode']
        assert "Leco GC-Tof" == json.loads(response['body'])["acquisition"]['instrument']
        assert "GCTOF" == json.loads(response['body'])["acquisition"]['name']
        assert "positive" == json.loads(response['body'])["acquisition"]['ionisation']
        assert "gcms" == json.loads(response['body'])["acquisition"]['method']
        assert "Medicago sativa" == json.loads(response['body'])["metadata"]['species']
        assert "aerial part" == json.loads(response['body'])["metadata"]['organ']


def test_create_success_minix(requireMocking):
    data = {"id": 63618}
    response = create.fromMinix({'body': json.dumps(data)}, {})

    assert 0 < len(response)

    for item in response:
        assert 'isBase64Encoded' in item
        assert 200 == item['statusCode']
        assert '63618' == json.loads(item['body'])['experiment']
        assert json.loads(item['body'])['id'] == json.loads(item['body'])['sample']


def test_create_non_minix(requireMocking):
    data = {
        'sample': 'test_no_minix',
        'experiment': '1',
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',
            'method': 'gcms'
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
            'comment': ''
        }
    }

    response = create.create({'body': json.dumps(data)}, {})

    assert 'isBase64Encoded' in response
    assert 200 == response['statusCode']
    assert 'body' in response
    assert 'test_no_minix' == json.loads(response['body'])['id']

    # checking creation of tracking data
    tracking = get.get({'pathParameters': {'sample': data['sample']}}, {})
    assert 'isBase64Encoded' in response
    assert 200 == tracking['statusCode']
    assert data['sample'] == json.loads(tracking['body'])['id']
    assert 'entered' == json.loads(tracking['body'])['status'][0]['value']

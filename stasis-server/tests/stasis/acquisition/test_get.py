import simplejson as json

from stasis.acquisition import get
from stasis.tables import TableManager


def test_get_no_reference(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_acquisition_table()
    table.put_item(Item={
        'sample': '180415dZKsa20_1',
        'experiment': '54321',
        'acquisition': {
            'instrument': 'Leco GC-Tof',
            'name': 'GCTOF',
            'ionisation': 'positive',
            'method': 'gcms'
        },
        'metadata': {
            'class': '382172',
            'species': 'rat',
            'organ': 'tissue'
        },
        'userdata': {
            'label': 'GP_S_6_006',
            'comment': ''
        },
        'time': 1525121375499,
        'id': '180415dZKsa20_1'
    })
    # process data

    result = get.get({
        "pathParameters": {
            "sample": "180415dZKsa20_1"
        }
    }, {})

    print(result)
    assert 200 == result['statusCode']
    assert "180415dZKsa20_1" == json.loads(result['body'])['id']
    assert "Leco GC-Tof" == json.loads(result['body'])['acquisition']['instrument']


def test_get_with_reference(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_acquisition_table()
    table.put_item(Item={
        'sample': '180415dZKsa20_1',
        'experiment': '12345',
        'acquisition': {
            'instrument': 'Leco GC-Tof',
            'name': 'GCTOF',
            'ionisation': 'positive',
            'method': 'gcms'
        },
        'metadata': {
            'class': '382172',
            'species': 'rat',
            'organ': 'tissue'
        },
        'userdata': {
            'label': 'GP_S_6_006',
            'comment': ''
        },
        'time': 1525121375499,
        'id': '180415dZKsa20_1',
        'references': [{
            'name': 'minix',
            'value': '12345'
        }]
    })

    # process data

    result = get.get({
        "pathParameters": {
            "sample": "180415dZKsa20_1"
        }
    }, {})

    print(result)
    assert result['statusCode'] == 200
    assert json.loads(result['body'])["id"] == "180415dZKsa20_1"
    assert json.loads(result['body'])["acquisition"]["instrument"] == "Leco GC-Tof"
    assert json.loads(result['body'])["references"][0]["name"] == "minix"
    assert json.loads(result['body'])["references"][0]["value"] == "12345"


def test_get_inexistent_sample():
    response = get.get("thereIsNoSpoon", {})

    print(response)

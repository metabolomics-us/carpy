import simplejson as json
from boto.dynamodb2.exceptions import ValidationException
from botocore.exceptions import ClientError
from jsonschema import validate
from pytest import fail

from stasis.acquisition import get
from stasis.schema import __ACQUISITION_SCHEMA__
from stasis.tables import TableManager


def test_get_no_reference(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_acquisition_table()

    item = {
        'id': '180415dZKsa20_1',
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
        'processing': {
            'method': 'gcms | test | test | positive'
        },
        'time': 1525121375499
    }

    try:
        validate(item, __ACQUISITION_SCHEMA__)
        table.put_item(Item=tm.sanitize_json_for_dynamo(item))
    except ValidationException as vex:
        result = None
        fail(str(vex.body))
    except ClientError as cer:
        result = None
        fail(str(cer.response))

    # process data
    result = get.get({
        "pathParameters": {
            "sample": "180415dZKsa20_1"
        }
    }, {})

    assert 200 == result['statusCode']
    assert "180415dZKsa20_1" == json.loads(result['body'])['id']
    assert "Leco GC-Tof" == json.loads(result['body'])['acquisition']['instrument']


def test_get_with_reference(requireMocking):
    # store data
    tm = TableManager()
    table = tm.get_acquisition_table()
    item = {
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
        'processing': {
            'method': 'gcms | test | test | positive'
        },
        'time': 1525121375499,
        'id': '180415dZKsa20_1',
        'references': [{
            'name': 'minix',
            'value': '12345'
        }]
    }
    try:
        validate(item, __ACQUISITION_SCHEMA__)
        table.put_item(Item=tm.sanitize_json_for_dynamo(item))
    except ValidationException as vex:
        result = None
        fail(str(vex.body))
    except ClientError as cer:
        result = None
        fail(str(cer.response))

    # process data

    result = get.get({
        "pathParameters": {
            "sample": "180415dZKsa20_1"
        }
    }, {})

    assert result['statusCode'] == 200
    assert json.loads(result['body'])["id"] == "180415dZKsa20_1"
    assert json.loads(result['body'])["acquisition"]["instrument"] == "Leco GC-Tof"
    assert json.loads(result['body'])["references"][0]["name"] == "minix"
    assert json.loads(result['body'])["references"][0]["value"] == "12345"


def test_get_inexistent_sample(requireMocking):
    response = get.get("thereIsNoSpoon", {})

    print(f'RESPONSE: {json.dumps(response, indent=2)}')

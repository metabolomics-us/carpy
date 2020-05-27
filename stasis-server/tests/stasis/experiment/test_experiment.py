import pytest
import simplejson as json
from boto.dynamodb2.exceptions import ValidationException
from botocore.exceptions import ClientError

from pytest import fail

from stasis.experiment import experiment
from stasis.tables import TableManager


@pytest.mark.parametrize('sample_count', [5, 10, 100, 1000])
def test_get_experiment(requireMocking, sample_count):
    tm = TableManager()
    table = tm.get_acquisition_table()

    try:
        for x in range(0, sample_count):
            table.put_item(Item=tm.sanitize_json_for_dynamo({
            "sample": f"test-{x:06d}",
            "experiment": "1",
            "id": f"test-{x:06d}",
            "acquisition": {
                "instrument": "random",
                "ionisation": "positive",
                "method": "test-method"
            },
            "metadata": {
                "class": f"{x%100}",
                "species": "rat",
                "organ": "tissue"
            },
            "userdata": {
                "label": "GP_S_6_006",
                "comment": ""
            },
            "processing": {
                "method": "test-method | random | test | positive"
            }
        }))
    except ValidationException as vex:
        result = None
        fail(str(vex.body))
    except ClientError as cer:
        result = None
        fail(str(cer.response))

    page_size = 3

    result = experiment.get({
        'pathParameters': {
            'experiment': '1',
            'psize': page_size
        }
    }, {})

    data = json.loads(result['body'])

    assert result['statusCode'] == 200
    assert len(data['items']) == page_size
    assert data['last_item']['id'] == 'test-000002'

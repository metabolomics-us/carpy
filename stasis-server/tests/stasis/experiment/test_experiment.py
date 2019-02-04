import pytest
import simplejson as json

from stasis.experiment import experiment
from stasis.tables import TableManager


@pytest.mark.parametrize('sample_count', [5, 10, 100, 1000, 10000])
def test_get_experiment(requireMocking, sample_count):
    tm = TableManager()
    table = tm.get_tracking_table()

    for x in range(0, sample_count):
        table.put_item(Item={
            "id": "test-{0:06d}".format(x),
            "experiment": "1",
            "sample": "test-{0:06d}".format(x),
            "status": [{"time": 1524772162698, "value": "PROCESSING", "fileHandle": "test.mzml"}]
        })

    page_size = 3

    result = experiment.get({
        'pathParameters': {
            'experiment': '1',
            'psize': page_size
        }
    }, {})

    data = json.loads(result['body'])

    assert 200 == result['statusCode']
    assert page_size == len(data['items'])
    assert 'test-000002' == data['last_item']['id']

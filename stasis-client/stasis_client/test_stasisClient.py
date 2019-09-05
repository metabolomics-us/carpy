import os
import unittest
from time import time

from stasis_client.client import StasisClient

url = "https://test-api.metabolomics.us/stasis"
key = os.getenv('STASIS_API_TOKEN')

client = StasisClient(url, key)


def _create_sample(name: str = 'test'):
    data = {
        'sample': '123-{}-{}'.format(name, time()),
        'experiment': 'mySecretExp_{}'.format(123),
        'acquisition': {
            'instrument': 'test inst',
            'ionisation': 'positive',
            'name': 'some name',
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
    return data


class TestStasisClient(unittest.TestCase):
    def test_sample_acquisition_create(self):

        data = _create_sample()
        result = client.sample_acquisition_create(data)
        self.assertEqual(200, result.status_code)

        result = client.sample_acquisition_get(data['sample'])
        self.assertEqual(data['sample'], result['sample'])

    def test_sample_state(self):

        sample = _create_sample('123')
        result = client.sample_state_update(sample['sample'], 'entered')

        self.assertEqual(200, result.status_code)
        self.assertEqual('entered', client.sample_state(sample['sample'])[0]['value'])

    def test_sample_result(self):

        result = client.sample_result('Zeki_SIMVA_test_1uL.mzml')
        print(result)
        self.assertIsNotNone(result)

    # def test_get_experiment():
    #
    #     samples = client.get_experiment('12345', [], )
    #     print(f'\nsamples ({len(samples)}): {samples}')
    #     assert samples is not None
    #     assert len(samples) == 10

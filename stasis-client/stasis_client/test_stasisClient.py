import os
import unittest
from time import time

from stasis_client.client import StasisClient

sample_time = time()


def _create_sample(name: str = 'test'):
    data = {
        'sample': '123-{}-{}'.format(name, sample_time),
        'experiment': f'mySecretExp_{123}',
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
    url = 'https://test-api.metabolomics.us/stasis'
    key = os.getenv('STASIS_API_TOKEN')
    client = StasisClient(url, key)

    def test_sample_acquisition_create(self):
        data = _create_sample()
        result = self.client.sample_acquisition_create(data)
        self.assertEqual(200, result.status_code, "Response didn't have OK status code")

        result = self.client.sample_acquisition_get(data['sample'])
        self.assertEqual(data['sample'], result['sample'])

    def test_acquisition_get(self):
        result = self.client.sample_acquisition_get(f'test_1')
        print(result)
        metadata = {'class': '123456',
                    'organ': 'tissue',
                    'species': 'rat'}
        self.assertEqual(metadata, result.get('metadata'))

    def test_sample_state(self):
        sample = _create_sample('123')
        result = self.client.sample_state_update(sample['sample'], 'entered')

        self.assertEqual(200, result.status_code, "Response didn't have OK status code")
        self.assertEqual('entered', self.client.sample_state(sample['sample'])[0]['value'])

    def test_sample_result(self):
        result = self.client.sample_result('lgvty_cells_pilot_2_POS_500K_01.json')

        self.assertIsNotNone(result)
        self.assertEqual('lgvty_cells_pilot_2_POS_500K_01', result['sample'])

    def test_inexistent_result(self):
        result = self.client.sample_result('blah.blah')
        print(f'RESULT: {result}')
        self.assertIn('Error', result, 'The response should have an "Error" key')
        self.assertEqual('blah.blah', result.get('filename'))

    def test_persist_inexistent_file(self):
        if os.path.exists('stfu/blah.blah'):
            os.remove('stfu/blah.blah')

        result = self.client.sample_result('blah.blah', 'stfu')
        self.assertIsNotNone(result['Error'])
        self.assertFalse(os.path.exists('stfu/blah.blah'))

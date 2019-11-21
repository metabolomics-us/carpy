#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pprint
import unittest

import pytest
from _pytest import monkeypatch
from requests import RequestException
from stasis_client.client import StasisClient

from scheduler.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    pp = pprint.PrettyPrinter(indent=4)

    def setUp(self):
        config = {'test': True,
                  'experiment': {
                      'chromatography': [{'method': 'teddy',
                                          'instrument': '6530',
                                          'column': 'test',
                                          'ion_mode': 'positive',
                                          'raw_files_list': 'samples-pos.csv',
                                          'raw_files': []},
                                         {'method': 'teddy',
                                          'instrument': '6550',
                                          'column': 'test',
                                          'ion_mode': 'negative',
                                          'raw_files_list': 'samples-neg.txt',
                                          'raw_files': []}
                                         ],
                      'metadata': {'species': 'human', 'organ': 'plasma'}
                  },
                  'task_version': 164,
                  'create_tracking': True,
                  'create_acquisition': True,
                  'schedule': True,
                  'env': 'test',
                  'additional_profiles': None
                  }
        self.mp = monkeypatch.MonkeyPatch()
        self.scheduler = Scheduler(config)
        self.scheduler.config['experiment']['name'] = 'teddy'
        self.scheduler.config['save_msms'] = False

    def test_api_token_with_test_env_set(self):
        token = self.scheduler._api_token()
        self.pp.pprint(token)
        self.assertIsNotNone(token['x-api-key'])
        self.assertTrue(token['x-api-key'].startswith('GU'))

    def test_api_token_with_prod_env_set(self):
        self.scheduler.config['test'] = False
        self.scheduler.token_var_name = 'PROD_STASIS_API_TOKEN'
        token = self.scheduler._api_token()
        self.pp.pprint(f'Token: {token}')
        self.assertIsNotNone(token['x-api-key'])
        self.assertTrue(token['x-api-key'].startswith('cW'))

    def test_api_token_without_env_set(self):
        envs = {
            self.scheduler.token_var_name: ''
        }
        self.mp.setattr(os, 'environ', envs)

        with pytest.raises(RequestException, match=r"Missing authorization token.*"):
            self.scheduler._api_token()

    def test_schedule_in_test_mode(self):
        self.assertEquals(200, self.scheduler.schedule('B2A_TeddyLipids_Pos_QC001',
                                                       self.scheduler.config['experiment']['chromatography']))

    def test_schedule_in_prod_mode(self):
        self.scheduler.config['test'] = False

        # running with inexistent name to avoid real processing
        self.assertEquals(200, self.scheduler.schedule('B2A_TeddyLipids_Pos_QC001x',
                                                       self.scheduler.config['experiment']['chromatography']))

    def test_add_tracking(self):
        data = {
            'sample': 'test-file',
            'experiment': 'test',
            'acquisition': {
                'instrument': 'QExactive',
                'ionisation': 'positive',
                'method': 'hilic'
            },
            'processing': {
                'method': 'hilic | QExactive | test | positive'
            },
            'metadata': {
                'species': 'human',
                'organ': 'plasma'
            }
        }
        self.scheduler.apiBase = 'https://test-api.metabolomics.us/stasis'
        self.scheduler.token_var_name = 'STASIS_API_TOKEN'
        self.scheduler.config['experiment']['name'] = 'test'
        self.scheduler.config['test'] = False

        stasis = StasisClient('https://test-api.metabolomics.us/stasis', os.getenv('STASIS_API_TOKEN'))
        stasis.sample_acquisition_create(data)

        self.scheduler.add_tracking('test-file')

        status = stasis.sample_state('test-file')
        self.pp.pprint(status)
        self.assertIsNotNone(status)
        self.assertEqual(3, len(status))

    # def test_get_experiment_aws(self):
    #     data = self.scheduler.get_experiment_aws('teddy')
    #
    #     self.assertIsNotNone(data)
    #     self.pp.pprint(f'size: {len(data)}')
    #     for sample in data:
    #         self.pp.pprint(f'{sample}\n------------------------------------------------\n')

    def test_multi_chromatography_methods(self):
        result = self.scheduler.process('../../resources')
        pprint.pprint(result)

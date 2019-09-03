#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

import pytest
from _pytest import monkeypatch
from requests import RequestException

from scheduler.scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def setUp(self):
        config = {'test': True,
                  'experiment': {
                      'chromatography': {},
                      'metadata': {'species': 'human', 'organ': 'plasma'}
                  }, 'task_version': 163,
                  'create_tracking': True,
                  'create_metadata': True,
                  'schedule': True,
                  'env': 'test',
                  'additional_profiles': None
                  }
        self.mp = monkeypatch.MonkeyPatch()
        self.scheduler = Scheduler(config)
        self.scheduler.config['experiment']['name'] = 'teddy'
        self.scheduler.config['experiment']['chromatography']['method'] = 'teddy'
        self.scheduler.config['experiment']['chromatography']['instrument'] = '6530'
        self.scheduler.config['experiment']['chromatography']['column'] = 'test'
        self.scheduler.config['experiment']['chromatography']['ion_mode'] = 'positive'
        self.scheduler.config['experiment']['chromatography']['save_msms'] = False
        self.scheduler.config['experiment']['chromatography']['raw_files_list'] = 'resources/samples.csv'

    def test_api_token_with_test_env_set(self):
        token = self.scheduler._api_token()
        print(token)
        self.assertIsNotNone(token['x-api-key'])
        self.assertTrue(token['x-api-key'].startswith('GU'))

    def test_api_token_with_prod_env_set(self):
        self.scheduler.config['test'] = False
        self.scheduler.token_var_name = 'PROD_STASIS_API_TOKEN'
        token = self.scheduler._api_token()
        print(f'Token: {token}')
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

        # running with inexistent name to avoid rel processing
        self.assertEquals(200, self.scheduler.schedule('B2A_TeddyLipids_Pos_QC001x',
                                                       self.scheduler.config['experiment']['chromatography']))


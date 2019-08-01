#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from argparse import Namespace

import pytest
from _pytest import monkeypatch
from requests import RequestException

from scheduler.scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def setUp(self):
        args = Namespace()
        args.test = True
        self.mp = monkeypatch.MonkeyPatch()
        self.scheduler = Scheduler(args)

    def test_api_token_with_env_set(self):
        token = self.scheduler._api_token()
        print(token)
        self.assertIsNotNone(token['x-api-key'])

    def test_api_token_without_env_set(self):
        envs = {
            self.scheduler.token_var_name: ''
        }
        self.mp.setattr(os, 'environ', envs)

        with pytest.raises(RequestException, match=r"Missing authorization token.*"):
            self.scheduler._api_token()

    def test_schedule(self):
        self.scheduler.args.extra_profiles = ''
        self.scheduler.args.test = True
        self.scheduler.args.method = 'teddy'
        self.scheduler.args.instrument = '6530'
        self.scheduler.args.experiment = 'teddy'
        self.scheduler.args.column = 'test'
        self.scheduler.args.ion_mode = 'positive'
        self.scheduler.args.task_version = '163'
        self.scheduler.args.env = 'test'

        filename = 'resources/samples.csv'
        self.assertEquals(200, self.scheduler.schedule(filename))

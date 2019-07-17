import logging
import unittest

import pandas as pd

import cragLauncher as launcher
from crag import stasis
from crag.aggregator import Aggregator

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)


class TestAggregator(unittest.TestCase):
    logger = logging.getLogger('DEBUG')

    def setUp(self):
        self.parser = launcher.create_parser()
        self.samples = ['B13A_TeddyLipids_Pos_QC002',
                        'B13A_SA11890_TeddyLipids_Pos_24G4N',
                        'B13A_SA11891_TeddyLipids_Pos_16LNW',
                        'invalid_sample',
                        'B13A_SA11893_TeddyLipids_Pos_1U9NP',
                        'B13A_SA11894_TeddyLipids_Pos_1MNF4']

    def test_find_intensity(self):
        # test find_intensity on non replaced data
        aggregator = Aggregator(self.parser.parse_args(['filename']))
        value = {'intensity': 1, 'replaced': False}
        self.assertEqual(1, aggregator.find_intensity(value))

        # test find_intensity on zero replaced data not requesting replaced data
        value = {'intensity': 2, 'replaced': True}
        self.assertEqual(0, aggregator.find_intensity(value))

        # test find_intensity on zero replaced data requesting replaced data
        aggregator = Aggregator(self.parser.parse_args(['filename', '-zr']))
        value = {'intensity': 2, 'replaced': True}
        self.assertEqual(2, aggregator.find_intensity(value))

    def test_find_replaced(self):
        self.assertEqual(2, Aggregator.find_replaced({'intensity': 2, 'replaced': True}))
        self.assertEqual(0, Aggregator.find_replaced({'intensity': 2, 'replaced': False}))

    def test_add_metadata(self):
        # Test correct indexing of samples in header

        aggregator = Aggregator(self.parser.parse_args(['filename', '-s', '-d', 'samples']))
        results = self.build_result()

        md = aggregator.add_metadata(self.samples, results)

        self.assertTrue(md.iloc[4, 6:].to_list() == list(range(1, 7)))

    def test_get_target_list(self):
        results = self.build_result()
        self.assertTrue(len(Aggregator.get_target_list(results)) > 0)
        self.assertEqual(964, len(Aggregator.get_target_list(results)))

    def test_build_worksheet(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']))
        results = self.build_result()
        targets = aggregator.get_target_list(results)
        intensity = aggregator.build_worksheet(targets, 'intensity matrix')
        self.assertEqual(len(targets), intensity.index.size)

    def test_process_sample_list(self):
        aggregator = Aggregator(self.parser.parse_args(['filename', '-s', '-d', 'samples']))
        aggregator.process_sample_list(self.samples, 'test')

    def build_result(self):
        results = []

        for sample in self.samples:
            data = stasis.get_file_results(sample, False, 'samples', True)
            data['sample'] = sample
            results.append(data)

        return results

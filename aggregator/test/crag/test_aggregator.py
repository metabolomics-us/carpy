import logging
import os
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

    def test_get_target_list_negative_mode(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']))
        self.samples = ['B7B_TeddyLipids_Neg_QC015',
                        'B12A_SA11202_TeddyLipids_Neg_1RXZX_2']
        results = self.build_result()
        targets = aggregator.get_target_list(results)

        self.assertTrue(len(targets) > 0)
        self.assertEqual(1228, len(targets))

    def test_get_target_list_positive_mode(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']))
        results = self.build_result()

        targets = aggregator.get_target_list(results)
        self.assertTrue(len(targets) > 0)
        self.assertEqual(964, len(targets), msg='# of positive mode targets should be 964')

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

    def test_build_worksheet(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']))
        results = self.build_result()
        targets = aggregator.get_target_list(results)
        intensity = aggregator.build_worksheet(targets, 'intensity matrix')
        self.assertEqual(len(targets), intensity.index.size)

    def test_process_sample_list(self):
        excel_list = {'intensity_matrix-test-results-norepl.xlsx',
                      'mass_matrix-test-results-norepl.xlsx',
                      'original_rt_matrix-test-results-norepl.xlsx',
                      'replaced_values-test-results-norepl.xlsx',
                      'retention_index_matrix-test-results-norepl.xlsx',
                      'correction_curve-test-results-norepl.xlsx'}

        aggregator = Aggregator(self.parser.parse_args(['filename', '-s', '-d', 'samples']))
        aggregator.process_sample_list(self.samples, 'test')
        [self.assertTrue(os.path.exists(f)) for f in excel_list]
        [os.remove(f) for f in excel_list]

    def build_result(self):
        results = []

        for sample in self.samples:
            data = stasis.get_file_results(sample, False, 'samples', True)
            data['sample'] = sample
            results.append(data)

        return results

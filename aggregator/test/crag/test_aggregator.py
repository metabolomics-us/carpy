import logging
import os
import unittest

import pandas as pd
from stasis_client.client import StasisClient

import cragLauncher as launcher
from crag.aggregator import Aggregator

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)


class TestAggregator(unittest.TestCase):
    logger = logging.getLogger('DEBUG')
    stasis = StasisClient('https://test-api.metabolomics.us/stasis', os.getenv('STASIS_API_TOKEN'), True)

    def setUp(self):
        self.parser = launcher.create_parser()
        self.samples = ['B13A_TeddyLipids_Pos_QC002',
                        'B13A_SA11890_TeddyLipids_Pos_24G4N',
                        'B13A_SA11891_TeddyLipids_Pos_16LNW',
                        'invalid_sample',
                        'B13A_SA11893_TeddyLipids_Pos_1U9NP',
                        'B13A_SA11894_TeddyLipids_Pos_1MNF4']

    def test_get_target_list_negative_mode(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']), self.stasis)
        self.samples = ['B7B_TeddyLipids_Neg_QC015',
                        'B12A_SA11202_TeddyLipids_Neg_1RXZX_2']
        results = self._build_result()
        self.assertGreater(len(results), 0)

        targets = aggregator.get_target_list(results)

        self.assertTrue(len(targets) > 0)
        self.assertEqual(1228, len(targets))

    def test_get_target_list_positive_mode(self):
        aggregator = Aggregator(self.parser.parse_args(['filename']), self.stasis)
        results = self._build_result()

        targets = aggregator.get_target_list(results)
        self.assertTrue(len(targets) > 0)
        self.assertEqual(964, len(targets), msg='# of positive mode targets should be 964')

    def test_find_intensity(self):
        # test find_intensity on non replaced data
        aggregator = Aggregator(self.parser.parse_args(['filename']), self.stasis)
        value = {'intensity': 1, 'replaced': False}
        self.assertEqual(1, aggregator.find_intensity(value))

        # test find_intensity on zero replaced data not requesting replaced data
        value = {'intensity': 2, 'replaced': True}
        self.assertEqual(0, aggregator.find_intensity(value))

        # test find_intensity on zero replaced data requesting replaced data
        aggregator = Aggregator(self.parser.parse_args(['filename', '-zr']), self.stasis)
        value = {'intensity': 2, 'replaced': True}
        self.assertEqual(2, aggregator.find_intensity(value))

    def test_find_replaced(self):
        self.assertEqual(2, Aggregator.find_replaced({'intensity': 2, 'replaced': True}))
        self.assertEqual(0, Aggregator.find_replaced({'intensity': 2, 'replaced': False}))

    def test_add_metadata(self):
        # Test correct indexing of samples in header

        aggregator = Aggregator(self.parser.parse_args(['filename', '-s', '-d', 'samples']), self.stasis)
        results = self._build_result()

        md = aggregator.add_metadata(self.samples, results)

        self.assertTrue(md.iloc[4, 6:].to_list() == list(range(1, 7)))

    def test_build_worksheet(self):
        aggregator = Aggregator(self.parser.parse_args(['./']), self.stasis)
        results = self._build_result()
        targets = aggregator.get_target_list(results)
        intensity = aggregator.build_worksheet(targets, 'intensity matrix')
        self.assertEqual(len(targets), intensity.index.size)

    def test_process_sample_list(self):
        excel_list = {'test-intensity_matrix-results-norepl.xlsx',
                      'test-mass_matrix-results-norepl.xlsx',
                      'test-original_rt_matrix-results-norepl.xlsx',
                      'test-replaced_values-results-norepl.xlsx',
                      'test-retention_index_matrix-results-norepl.xlsx',
                      'test-correction_curve-results-norepl.xlsx',
                      'test-msms_spectrum-results-norepl.xlsx'}

        self.samples = ['lgvty_cells_pilot_2_NEG_50K_BR_01',
                        'lgvty_cells_pilot_2_NEG_50K_BR_03',
                        'lgvty_cells_pilot_2_NEG_50K_BR_05']

        aggregator = Aggregator(self.parser.parse_args(['samples/test.txt', '-d', 'samples']), self.stasis)
        aggregator.process_sample_list(self.samples, 'samples/test.txt')

        for f in excel_list:
            try:
                self.assertTrue(os.path.exists(f'samples/{f}'))
            except AssertionError as ae:
                print(f'{f} does not exist')
                raise AssertionError(ae)
            os.remove(f'samples/{f}')

    def test_format_sample(self):
        sample = 'lgvty_cells_pilot_2_NEG_50K_BR_01'
        samplefile = 'lgvty_cells_pilot_2_NEG_50K_BR_01.json'
        aggregator = Aggregator(self.parser.parse_args(['filename', '-s', '-d', 'samples']), self.stasis)
        result = self.stasis.sample_result(samplefile, 'samples')

        formatted = aggregator.format_sample(result)

        self.assertEqual('197.152847:5004.77979', formatted[7][sample][0])

    def _build_result(self):
        results = []

        for sample in self.samples:
            filename = os.path.splitext(sample)[0] + '.json'

            data = self.stasis.sample_result(filename)
            data['sample'] = sample
            if data.get('Error') is None:
                results.append(data)
            else:
                results.append({sample: {}})

        return results

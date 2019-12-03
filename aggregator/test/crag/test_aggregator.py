import logging
import os

import pandas as pd

import cragLauncher as launcher
from crag.aggregator import Aggregator

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)

logger = logging.getLogger('DEBUG')

parser = launcher.create_parser()
samples = ['B13A_TeddyLipids_Pos_QC002',
           'B13A_SA11890_TeddyLipids_Pos_24G4N',
           'B13A_SA11891_TeddyLipids_Pos_16LNW',
           'invalid_sample',
           'B13A_SA11893_TeddyLipids_Pos_1U9NP',
           'B13A_SA11894_TeddyLipids_Pos_1MNF4']

samples2 = ['B7B_TeddyLipids_Neg_QC015',
            'B12A_SA11202_TeddyLipids_Neg_1RXZX_2']


def test_get_target_list_negative_mode(stasis):
    aggregator = Aggregator(parser.parse_args(['filename']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()

    results = _build_result(stasis, samples2)
    assert len(results) > 0

    targets = aggregator.get_target_list(results)

    assert len(targets) > 0
    assert 1228 == len(targets)


def test_get_target_list_positive_mode(stasis):
    aggregator = Aggregator(parser.parse_args(['filename']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    results = _build_result(stasis, samples)

    targets = aggregator.get_target_list(results)
    assert len(targets) > 0
    assert 964 == len(targets)


def test_find_intensity(stasis):
    # test find_intensity on non replaced data
    aggregator = Aggregator(parser.parse_args(['filename']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    value = {'intensity': 1, 'replaced': False}
    assert 1 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data not requesting replaced data
    value = {'intensity': 2, 'replaced': True}
    assert 0 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data requesting replaced data
    aggregator = Aggregator(parser.parse_args(['filename', '-zr']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    value = {'intensity': 2, 'replaced': True}
    assert 2 == aggregator.find_intensity(value)


def test_find_replaced():
    assert 2 == Aggregator.find_replaced({'intensity': 2, 'replaced': True})
    assert 0 == Aggregator.find_replaced({'intensity': 2, 'replaced': False})


def test_add_metadata(stasis):
    # Test correct indexing of samples in header

    aggregator = Aggregator(parser.parse_args(['filename', '-s', '-d', 'samples']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    results = _build_result(stasis, samples)

    md = aggregator.add_metadata(samples, results)

    assert md.iloc[4, 6:].to_list() == list(range(1, 7))


def test_build_worksheet(stasis):
    aggregator = Aggregator(parser.parse_args(['./']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()

    results = _build_result(stasis, samples)
    targets = aggregator.get_target_list(results)
    intensity = aggregator.build_worksheet(targets, 'intensity matrix')
    assert len(targets) == intensity.index.size


def test_process_sample_list(stasis):
    excel_list = {'test-intensity_matrix-results-norepl.xlsx',
                  'test-mass_matrix-results-norepl.xlsx',
                  'test-original_rt_matrix-results-norepl.xlsx',
                  'test-replaced_values-results-norepl.xlsx',
                  'test-retention_index_matrix-results-norepl.xlsx',
                  'test-correction_curve-results-norepl.xlsx',
                  'test-msms_spectrum-results-norepl.xlsx'}

    samples = ['lgvty_cells_pilot_2_NEG_50K_BR_01',
               'lgvty_cells_pilot_2_NEG_50K_BR_03',
               'lgvty_cells_pilot_2_NEG_50K_BR_05']

    aggregator = Aggregator(parser.parse_args(['samples/test.txt', '-d', 'samples']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    aggregator.process_sample_list(samples, 'samples/test.txt')

    for f in excel_list:
        try:
            assert os.path.exists(f'samples/{f}')
        except AssertionError as ae:
            print(f'{f} does not exist')
            raise AssertionError(ae)
        os.remove(f'samples/{f}')


def test_format_sample(stasis):
    sample = 'lgvty_cells_pilot_2_NEG_50K_BR_01'
    samplefile = 'lgvty_cells_pilot_2_NEG_50K_BR_01.json'
    aggregator = Aggregator(parser.parse_args(['filename', '-s', '-d', 'samples']), stasis)
    assert "https://test-api.metabolomics.us/stasis" == aggregator.stasis_cli.get_url()
    result = stasis.sample_result(samplefile, 'samples')

    formatted = aggregator.format_sample(result)

    assert '197.152847:5004.77979' == formatted[7][sample][0]


def _build_result(stasis, locsamples):
    results = []

    for sample in locsamples:
        filename = os.path.splitext(sample)[0] + '.json'

        data = stasis.sample_result(filename)
        data['sample'] = sample
        if data.get('Error') is None:
            results.append(data)
        else:
            results.append({sample: {}})

    return results

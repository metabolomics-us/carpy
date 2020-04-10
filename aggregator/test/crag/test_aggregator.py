import logging
import os

import pandas as pd
from pytest import fail

from bin import crag_local
from crag.aggregator import Aggregator

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)

logger = logging.getLogger('DEBUG')

parser = crag_local.create_parser()
samples = ['B13A_TeddyLipids_Pos_QC002',
           'B13A_SA11890_TeddyLipids_Pos_24G4N',
           'B13A_SA11891_TeddyLipids_Pos_16LNW',
           'invalid_sample',
           'B13A_SA11893_TeddyLipids_Pos_1U9NP',
           'B13A_SA11894_TeddyLipids_Pos_1MNF4']

samples2 = ['B7B_TeddyLipids_Neg_QC015',
            'B12A_SA11202_TeddyLipids_Neg_1RXZX_2']


def test_get_target_list_negative_mode(stasis):
    aggregator = Aggregator({'infile': 'filename'}, stasis)

    results = _build_result(stasis, samples2)
    assert len(results) > 0

    targets = aggregator.get_target_list(results)

    assert len(targets) > 0
    assert 1228 == len(targets)


def test_get_target_list_positive_mode(stasis):
    aggregator = Aggregator({'infile': 'filename'}, stasis)
    results = _build_result(stasis, samples)

    targets = aggregator.get_target_list(results)
    assert len(targets) > 0
    assert 964 == len(targets)


def test_find_intensity(stasis):
    # test find_intensity on non replaced data
    aggregator = Aggregator({'infile': 'filename'}, stasis)
    value = {'intensity': 1, 'replaced': False}
    assert 1 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data not requesting replaced data
    value = {'intensity': 2, 'replaced': True}
    assert 0 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data requesting replaced data
    aggregator = Aggregator({'infile': 'filename', 'zero_replacement': True}, stasis)
    value = {'intensity': 2, 'replaced': True}
    assert 2 == aggregator.find_intensity(value)


def test_find_replaced():
    assert 2 == Aggregator.find_replaced({'intensity': 2, 'replaced': True})
    assert 0 == Aggregator.find_replaced({'intensity': 2, 'replaced': False})


def test_add_metadata(stasis):
    # Test correct indexing of samples in header

    aggregator = Aggregator({'infile': 'filename', 'save': True, 'dir': 'samples'}, stasis)
    results = _build_result(stasis, samples)

    md = aggregator.add_metadata(samples, results)

    assert md.iloc[4, 6:].to_list() == list(range(1, 7))


def test_build_worksheet(stasis):
    aggregator = Aggregator({'infile': './'}, stasis)

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

    aggregator = Aggregator({'infile': 'samples/test.txt', 'dir': 'samples'}, stasis)
    aggregator.process_sample_list(samples, 'samples/test.txt')


def test_format_sample(stasis):
    sample = 'lgvty_cells_pilot_2_NEG_50K_BR_01'
    samplefile = 'lgvty_cells_pilot_2_NEG_50K_BR_01'
    aggregator = Aggregator({'infile': 'filename', 'save': True, 'dir': 'samples'}, stasis)
    result = stasis.sample_result_as_json(samplefile)

    formatted = aggregator.format_sample(result)

    assert '197.152847:5004.77979' == formatted[7][sample][0]


def _build_result(stasis, locsamples):
    results = []

    for sample in locsamples:
        filename = os.path.splitext(sample)[0]

        data = stasis.sample_result_as_json(filename)
        if data is not None:
            data['sample'] = sample
            results.append(data)
        else:
            results.append({sample: {}})

    return results


def test_aggregate(stasis):
    aggregator = Aggregator(args=parser.parse_args(['test/test.txt']), stasis=stasis)
    aggregator.aggregate()


def test_aggregate_file_not_found(stasis):
    aggregator = Aggregator(args=parser.parse_args(['bad.txt']), stasis=stasis)
    try:
        aggregator.aggregate()
        fail()
    except FileNotFoundError:
        pass


def test_aggregate_no_args(stasis):
    aggregator = Aggregator({}, stasis)

    try:
        aggregator.aggregate()
        fail()
    except KeyError:
        pass


def test_aggregate_sample_only(stasis):
    aggregator = Aggregator({}, stasis)

    aggregator.aggregate_samples(samples=samples)

import logging
import os
from pathlib import Path

import pandas as pd
from pytest import fail

from bin import crag_local
from crag.aggregator import Aggregator

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)

logger = logging.getLogger('DEBUG')

parser = crag_local.create_parser()
samples = ['PlasmaBiorec001_MX524916_posCSH_preSOP001',
           'PlasmaBiorec002_MX524916_posCSH_postSOP010',
           'invalid_sample',
           'PlasmaPoolQC001_MX524916_posCSH_preSOP001',
           'PlasmaPoolQC002_MX524916_posCSH_postSOP010']

samples2 = ['SOP_Plasma_PoolMSMS_002_MX524916_negCSH_700_800',
            'SOP_Plasma_PoolMSMS_003_MX524916_negCSH_800_880']

parent = Path(__file__).resolve().parent


def test_get_target_list_negative_mode(stasis):
    aggregator = Aggregator({'infiles': 'filename'}, stasis)

    results = _build_result(stasis, samples2)
    assert len(results) > 0

    targets = aggregator.get_target_list(results)
    assert len(targets) > 0


def test_get_target_list_positive_mode(stasis):
    aggregator = Aggregator({'infiles': 'filename'}, stasis)
    results = _build_result(stasis, samples)

    targets = aggregator.get_target_list(results)
    assert len(targets) > 0


def test_find_intensity(stasis):
    # test find_intensity on non replaced data
    aggregator = Aggregator({'infiles': 'filename'}, stasis)
    value = {'intensity': 1, 'replaced': False}
    assert 1 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data not requesting replaced data
    value = {'intensity': 2, 'replaced': True}
    assert 2 == aggregator.find_intensity(value)

    # test find_intensity on zero replaced data requesting replaced data
    aggregator = Aggregator({'infiles': 'filename', 'exclude_replacement': True}, stasis)
    value = {'intensity': 2, 'replaced': True}
    assert 0 == aggregator.find_intensity(value)


def test_find_replaced():
    assert 2 == Aggregator.find_replaced({'intensity': 2, 'replaced': True})
    assert 0 == Aggregator.find_replaced({'intensity': 2, 'replaced': False})


def test_add_metadata(stasis):
    # Test correct indexing of samples in header

    aggregator = Aggregator({'infiles': 'filename', 'save': True, 'dir': f'{parent}/../data'}, stasis)
    results = _build_result(stasis, samples)

    md = aggregator.add_metadata(samples, results)

    assert md.iloc[4, 6:].to_list() == list(range(1, 6))


def test_build_worksheet(stasis):
    aggregator = Aggregator({'infiles': 'filename'}, stasis)

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

    samples = ['PlasmaBiorec001_MX524916_posCSH_preSOP001',
               'PlasmaBiorec002_MX524916_posCSH_postSOP010',
               'PlasmaBiorec003_MX524916_posCSH_postSOP020']

    aggregator = Aggregator({'infiles': 'filename'}, stasis)
    aggregator.process_sample_list(samples, f'{parent}/../results')


def test_format_sample(stasis):
    sample = 'PNACIC_UnkLip_IntQC_P2_QE_A_NEG_14Oct20_Lola-WCSH315112'
    samplefile = 'PNACIC_UnkLip_IntQC_P2_QE_A_NEG_14Oct20_Lola-WCSH315112'
    aggregator = Aggregator({'infile': 'filename', 'save': True}, stasis)
    result = stasis.sample_result_as_json(samplefile)

    formatted = aggregator.format_sample(result)

    assert '152.994812:7832.22 158.026062:7178.55 172.474503:3949.74 187.616302:4657.92 ' \
           '202.055176:16934.99 231.554276:4670.40 237.226807:3772.17 254.032379:4215.71 ' \
           '269.248138:149924.94 292.144012:3959.56 339.703491:4769.80 ' \
           '368.308716:4431.29 437.528534:4201.56 502.319580:122849.00 ' \
           '532.803040:4007.13 631.061951:4249.08' == formatted[7][sample][74]


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
    aggregator = Aggregator({'infiles': [f'{parent}/../test.txt'], 'dir': f'{parent}/../data'}, stasis)
    aggregator.aggregate()


def test_aggregate_norepl(stasis):
    aggregator = Aggregator({'infiles': [f'{parent}/../test.txt'], 'dir': f'{parent}/../data',
                             'exclude_replacement': True}, stasis)
    aggregator.aggregate()


def test_aggregate_extra_files(stasis):
    aggregator = Aggregator({'infiles': [f'{parent}/../test.txt'], 'dir': f'{parent}/../data',
                             'extra_files': True}, stasis)
    aggregator.aggregate()


def test_aggregate_file_not_found(stasis):
    aggregator = Aggregator(args=parser.parse_args(['--files', 'bad.txt']), stasis=stasis)
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
    aggregator = Aggregator(args=parser.parse_args(['--dir', f'{parent}/../data']), stasis=stasis)

    aggregator.aggregate_samples(samples=samples, destination=f"{parent}/../results")

#!/usr/bin/env python

import io
import math
import pandas as pd
import re


def gaussian_similarity(actual, reference, tolerance):
    return math.exp(-0.5 * pow((actual - reference) / tolerance, 2))


def mass_similarity(x, tolerance):
    return gaussian_similarity(x['mz tgt'], x['opt mz'], tolerance)


def rt_similarity(x, tolerance):
    return gaussian_similarity(x['ri tgt(s)'], x['opt rt (s)'], tolerance)


def peak_similarity(x, mz_tolerance, rt_tolerance):
    return (mass_similarity(x, mz_tolerance) + rt_similarity(x, rt_tolerance)) / 2


if __name__ == '__main__':
    with open('Weiss005_posHILIC_40298234_039_target_options.csv') as f:
        data = f.read()

    # Remove Some()
    data = re.sub(r'Some\((\d+\.\d*)\)', r'\1', data)
    data = '\n'.join(
        x.replace('Some(', '', 1).replace('),', ',', 1) if i > 0 else x for i, x in enumerate(data.splitlines()))

    df = pd.read_csv(io.StringIO(data))
    df = df.dropna()
    # df = df.rename(columns={'ri tgt(s)': 'mz tgt', 'mz tgt': 'ri tgt(s)'})

    for i, row in df.iterrows():
        print('%0.4f' % peak_similarity(row, 0.01, 12), \
              '%0.4f' % row['mz tgt'], '%0.4f' % row['opt mz'], \
              '%0.4f' % row['ri tgt(s)'], '%0.4f' % row['opt rt (s)'], \
              row['tgt name'], sep='\t')

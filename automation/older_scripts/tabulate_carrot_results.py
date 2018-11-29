#!/usr/bin/env python

import argparse
import pandas as pd
import os
import glob
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', default='', type=str, help='flat result files to transform', nargs='*')
    parser.add_argument('-t', '--task', default='', type=str, help='Name of the task submitted')
    parser.add_argument('-s', '--submitter', default='', type=str, help='Submitter\'s email')
    parser.add_argument('-i', '--input', default=f'{Path.home()}/.carrot_storage')
    args = parser.parse_args()

    if(args.files != ''):
        files = args.files
    elif(args.task != '' and args.submitter != ''):
        path = args.input + '/'+ args.submitter + '_' + args.task
        files = [f for f in glob.glob(path)]
    else:
        print(args.help())
        exit(1)

    for f in files:
        df = pd.read_csv(f, encoding="utf-8", dtype={'filename': str, 'target': str,
                                                     'found at correction': bool, 'correction failed': bool,
                                                     'replaced value': bool, 'retention index (target)': float,
                                                     'mass (target)': float, 'retention index (annotation)': float,
                                                     'mass (annotation)': float, 'retention index shift': float,
                                                     'mass shift (mDa)': float, 'mass shift (ppm)': float,
                                                     'retention time (s)(annotation)': float,
                                                     'retention time (min)(annotation)': float,
                                                     'height (annotation)': float})
        grouped = df.groupby('filename')

        df = None

        for name, group in grouped:
            group = group.set_index(['target'])
            group = group.rename({'height (annotation)': name, 'mass (target)': 'mass', 'retention index (target)': 'retention time (s)'}, axis=1)
            group.loc[:, 'retention time (min)'] = group['retention time (s)'] / 60
            group = group[['mass', 'retention time (s)', 'retention time (min)', name]]
            group = group.transpose()

            if df is None:
                df = group
            else:
                df = df.append(group[group.index == name])

        df.to_csv(f.rsplit('.', 1)[0] +'_tabulated.csv')
        print(f'{f} is tabulated')
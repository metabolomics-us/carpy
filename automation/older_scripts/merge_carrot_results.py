#!/usr/bin/env python

import argparse
import glob
import os
import pandas as pd
from pathlib import Path


def export_msflo(df):
    df = df.transpose()
    df = df.rename({'target': 'Metabolite Name', 'mass': 'Average Mz', 'retention time (min)': 'Average Rt(min)'},
                   axis=1)

    df['Metabolite name'] = df.index
    df['Alignment Id'] = pd.Series(range(1, len(df.index) + 1), index=df.index)
    df = df.set_index('Alignment Id')

    preCols = ['Metabolite name', 'Average Mz', 'Average Rt(min)', 'retention time (s)']
    predf = df[preCols]
    df.drop(preCols, axis=1, inplace=True)
    print(predf.columns)
    sdf = pd.concat([predf, df], axis=1)
    sdf.to_csv(args.output.replace('merged', 'msflo'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default=f'{Path.home()}/.carrot_storage', help='Input directory')
    parser.add_argument('-o', '--output', default='', help='Output file name')
    parser.add_argument('-t', '--task', help='Name of the task. (Can contain wildcards)')
    parser.add_argument('-s', '--submitter', help='Submitter\'s email')
    args = parser.parse_args()

    if (args.output == ''):
        args.output = args.input + '/' + args.submitter + '_' + args.task.replace('*', '') + '_merged.csv'
    else:
        filename, ext = os.path.splitext(args.output)
        args.output = filename + '_merged.csv'

    print(f'input: {args.input}\noutput: {args.output}\ntask: {args.task}\nsubmitter: {args.submitter}')

    path = args.input + '/' + args.submitter + '_' + args.task + '_tabulated.csv'
    files = glob.glob(path)

    df_list = []
    wrong = []
    for idx, file in zip(range(0, len(files)), sorted(files)):
        print(f'Merging {file}')
        single = pd.read_csv(file, encoding='utf-8', index_col=0)
        single.index.name = 'target'
        df_list.append(single)

    full_df = pd.concat(df_list)
    full_df.drop_duplicates(inplace=True)
    header = full_df.loc[['mass', 'retention time (min)', 'retention time (s)']]

    body = full_df.drop(labels=['mass', 'retention time (min)', 'retention time (s)'])
    body = body.sort_index()
    full_df = pd.concat([header, body])

    sorted = full_df[sorted(full_df.columns)]
    sorted.to_csv(args.output)

    export_msflo(sorted)

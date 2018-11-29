#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', type=int, default=1, help='number of segments into which to split samples')
    parser.add_argument('files', type=str, nargs='+', default='__unknown__')

    args = parser.parse_args()
    if args.files == '__unknown__':
        print(parser.print_help())
        SystemExit('Missing file to process')

    segments = args.n
    samples = []

    for file in args.files:
        with open(file, 'r') as f:
            samples.extend([l for l in f.readlines() if l != '' and l[0:3] not in ['Q:\\', 'R:\\', 'Bat']])

    samples_copy = samples.copy()

    items_per_segment = round(len(samples)/segments)
    output = {}
    acc = 0
    last_c = 0
    for c in range(segments):
        output[f'segment_{c}'] = samples_copy[0+c:items_per_segment+c]
        acc = acc + len(output[f'segment_{c}'])
        [samples_copy.remove(x) for x in output[f'segment_{c}']]
        last_c = c

    output[f'segment_{last_c+1}'] = samples_copy

    for k in output:
        filename = f'./output/{k}.txt'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as fout:
            fout.writelines(output[k])

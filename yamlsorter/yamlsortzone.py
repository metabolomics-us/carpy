import argparse
import csv
from os.path import splitext
from pprint import pprint

import yaml

fields = ['accurateMass', 'identifier', 'retentionTime', 'targetType']


def readyaml(file):
    with open(file, 'r') as infile:
        result = yaml.load(infile)

    return result


def read_csv(file):
    yield


def calc_zone(t, zones: list):
    print(f'sorted: {zones}')
    rt = t['retentionTime']

    if t['retentionTimeUnit'] == 'seconds':
        rt = rt / 60

    for idx in range(0, len(zones)):
        if zones[idx] <= rt < zones[idx + 1]:
            print(f'{zones[idx]} <= {rt} < {zones[idx + 1]} -> zone: {idx}')
            # return idx-1
        idx += 1

    if 'zone' in t and t['zone'] > 0:
        return t['zone']
    else:
        return 0


def save_file(data, params):
    pprint(params)
    outfile = splitext(params['infile'])[0]
    outfile = outfile + '.sorted.' + params['outformat']

    if params['outformat'] == 'yaml':
        save_yaml(data, outfile)
    elif params['outformat'] == 'csv':
        save_csv(data, outfile)


def save_yaml(data, outfile):
    with open(outfile, 'w') as ofile:
        yaml.dump(data, ofile)


def save_csv(data, outfile):
    with open(outfile, 'w', newline='') as ofile:
        wr = csv.writer(ofile, lineterminator='\n', dialect='excel')
        wr.writerow(['name', 'instrument', 'column', 'ionMode', 'minimumPeakIntensity', 'description',
                     'identifier', 'accurateMass', 'retentionTime', 'retentiontimeUnit', 'targetType',
                     'requiredForCorrection', 'msms'])

        for a in data['config']:
            for t in a['targets']:
                wr.writerow([a['name'], a['instrument'], a['column'], a['ionMode'], a['minimumPeakIntensity'],
                             a['description'], t['identifier'], t['accurateMass'], t['retentionTime'],
                             t['retentionTimeUnit'], t['targetType'], t['requiredForCorrection'], t['msms']])


def process(params):
    data = readyaml(params['infile'])
    zones = [float(x) for x in params['zones'].split(',')]
    if 0.0 not in zones:
        zones.append(0.0)
    zones.sort()
    print(f'input: {zones}')

    for method in data:
        for config in data[method]:
            targets = sorted(config['targets'], key=lambda item: item[params['field']])
            for t in targets:
                t['zone'] = calc_zone(t, zones)

            config['targets'] = targets

    save_file(data, params)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sort yaml libs.')
    parser.add_argument('-i', '--infile', type=str,
                        help='input file. Example: /home/user/file.yml')
    parser.add_argument('-f', '--field', default='identifier', dest='field',
                        choices=['accurateMass', 'identifier', 'retentionTime', 'targetType'],
                        help='field to sort on.')
    parser.add_argument('--informat', default='yaml', dest='informat',
                        choices=['yaml', 'csv'],
                        help='input file format. default "yaml"')
    parser.add_argument('--outformat', default='yaml', dest='outformat',
                        choices=['yaml', 'csv'],
                        help='output file format. Default "yaml"')
    parser.add_argument('--zones',
                        help='Comma separated list of retention times (minutes) defining zones. '
                             'Example: 0.0,3.0,5.5,9.0,15.0')

    args = parser.parse_args()

    try:
        process(vars(args))
    except Exception as e:
        pprint(e.args)
        parser.print_help()
        exit(-1)

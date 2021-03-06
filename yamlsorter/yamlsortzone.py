import argparse
import csv
import sys
from os.path import splitext
from pprint import pprint

import yaml

fields = ['accurateMass', 'identifier', 'retentionTime', 'targetType']


def readyaml(file):
    with open(file, 'r') as infile:
        result = yaml.load(infile)

    return result


def read_csv(file):
    with open(file, 'r') as infile:
        cr = csv.reader(infile, dialect='excel')
        data = {'config': []}

        for t in cr:
            if t[0] == 'name':
                continue

            target = {'identifier': t[6], 'accurateMass': float(t[7]), 'retentionTime': float(t[8]),
                      'retentionTimeUnit': t[9], 'targetType': t[10], 'requiredForCorrection': bool(t[11]),
                      'zone': int(t[12]), 'msms': t[13]}

            lib = {}
            for item in data['config']:
                if item['name'] == t[0] and item['instrument'] == t[1] and item['column'] == t[2] \
                        and item['ionMode'] == t[3]:
                    lib = item
                    break

            if lib == {}:
                lib = {'name': t[0], 'instrument': t[1], 'column': t[2], 'ionMode': t[3], 'minimumPeakIntensity': int(t[4]),
                       'description': t[5], 'targets': []}
                data['config'].append(lib)

            lib['targets'].append(target)

    return data


def calc_zone(method, t, zones: dict):
    libname = f'{method["name"]} | {method["instrument"]} | {method["column"]} | {method["ionMode"]}'
    zone = zones[libname] if libname in zones else []

    try:
        rt = float(t['retentionTime'])
        # if 'zone' in t and int(t['zone']) > 0:
        #     return int(t['zone'])

        if t['retentionTimeUnit'] == 'seconds':
            rt = rt / 60

        if len(zone) == 0:
            return 0

        for idx in range(0, len(zone)):
            if zone[idx] <= rt < zone[idx + 1]:
                return idx
            idx += 1
    except TypeError as e:
        print(f"TypeError in t {t}")


def save_file(data, params):
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
                     'requiredForCorrection', 'zone', 'msms'])

        for a in data['config']:
            for t in a['targets']:
                wr.writerow([a['name'], a['instrument'], a['column'], a['ionMode'], int(a['minimumPeakIntensity']),
                             a['description'], t['identifier'], float(t['accurateMass']), float(t['retentionTime']),
                             t['retentionTimeUnit'], t['targetType'], bool(t['requiredForCorrection']), int(t['zone']),
                             t['msms']])


def process(params):
    data = []
    if str(params['infile']).lower().endswith('.csv'):
        data = read_csv(params['infile'])
    elif str(params['infile']).lower().endswith(('.yml', '.yaml')):
        data = readyaml(params['infile'])
    zones = params['zones']

    for section in data:
        for method in data[section]:
            targets = sorted(method['targets'], key=lambda item: item[params['field']])
            for t in targets:
                t['zone'] = calc_zone(method, t, zones)

            method['targets'] = targets

    save_file(data, params)


class keyvalue(argparse.Action):
    # Constructor calling
    def __call__(self, parser, namespace,
                 values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            # split it into key and value
            key, value = value.split(':')

            # assign into dictionary
            getattr(namespace, self.dest)[key] = [float(x) for x in value.split(',')] if len(value) > 0 else [0.0, 15.0]


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
    parser.add_argument('--zones', nargs='*', action=keyvalue,
                        help='Library definition of retention time zones.\n'
                             'Where ZONE has the format: <library name>:0.0,3.1,5.5,9.0,15.0')

    args = parser.parse_args()

    params = vars(args)

    for z in params['zones']:
        if 0.0 not in params['zones'][z]:
            params['zones'][z].append(0.0)

        params['zones'][z].sort()

    try:
        process(params)
    except argparse.ArgumentError as e:
        print(e)
        parser.print_help()
        exit(-1)

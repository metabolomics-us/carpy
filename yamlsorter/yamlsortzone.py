import yaml
from os.path import splitext
import argparse

fields = ['accurateMass', 'identifier', 'retentionTime', 'targetType']


def process(params):
    with open(params['infile'], 'r') as file:
        result = yaml.load(file)

        for method in result:
            for config in result[method]:
                targets = sorted(config['targets'], key=lambda item: item[params['field']])
                for t in targets:
                    if 'zone' not in t:
                        t['zone'] = 0

                config['targets'] = targets

        outfile, ext = splitext(params['infile'])
        with open(f"{outfile}.sorted{ext}", 'w') as ofile:
            yaml.dump(result, ofile)


parser = argparse.ArgumentParser(description='Sort yaml libs.')
parser.add_argument('-i', '--infile', type=str,
                    help='input file. Example: /home/user/file.yml')
parser.add_argument('-f', '--field', default='identifier',
                    choices=['accurateMass', 'identifier', 'retentionTime', 'targetType'],
                    help='field to sort on.')

args = parser.parse_args()

try:
    process(vars(args))
except Exception as e:
    parser.print_help()
    exit(-1)

import argparse
import pandas as pd
from ruamel.yaml import YAML

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file',
                        help='csv file with the list of targets with headers: '
                             'Metabolite name,Average Mz,Average Rt(min),istd')
    parser.add_argument('-o', '--output', help='name of the yml file to be created')
    parser.add_argument('-s', '--study', help='name of the study', required=True)
    parser.add_argument('-i', '--instrument', help='name of the instrument for the library', required=False, default = 'test')
    parser.add_argument('-c', '--column', help='name of the column for the library', required=False, default = 'test')
    parser.add_argument('-m', '--mode', help='ion mode. [\'positive\' or \'negative\']', required=False,
                        default = 'positive', choices=['positive','negative'])

    args = parser.parse_args()
    if args.file == '__unknown__' or args.study == "__unknown__":
        parser.print_help()
        SystemExit()

    df = pd.read_csv(args.file, usecols=['Metabolite name', 'Average Mz', 'Average Rt(min)', 'istd'])
    cols = list(df.columns.values)

    targets = []
    for target in df.to_dict(orient='records'):
        print('target: ' + str(target))

        t = {'identifier': f'{target["Metabolite name"]}',
             'accurateMass': target["Average Mz"],
             'retentionTime': target["Average Rt(min)"],
             'retentionTimeUnit': "minutes",
             'isInternalStandard': target['istd'],
             'requiredForCorrection': False,
             'confirmed': target['istd']}
        targets.append(t)

    print('---------------------------------')

    corrConfig = [{
        'name': args.study,
        'description': "",
        'column': args.column,
        'ionMode': args.mode,
        'instrument': args.instrument,
        'minimumPeakIntensity': 10000,
        'targets': [t for t in targets if t['isInternalStandard']]
    }]

    annotConfig = [{
        'name': args.study,
        'description': "",
        'column': args.column,
        'ionMode': args.mode,
        'instrument': args.instrument,
        'minimumPeakIntensity': 10000,
        'targets': [t for t in targets if not t['isInternalStandard']]
    }]

    library = {
        'carrot': {
            'lcms': {
                'correction': {'config': corrConfig},
                'annotation': {'config': annotConfig}
            }
        }
    }

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(sequence=4, offset=2)

    # open output file: 'application-carrot.lcms.yml'
    with open(args.output, 'w') as file:
        yaml.dump(library, file)

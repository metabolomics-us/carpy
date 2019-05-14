import argparse

import pandas as pd
from ruamel.yaml import YAML


def calculate_formate(t):
    """
    Creates a Formate adduct [M+FA-H]- from Acetate target (difference: −16.030202 Da)
    :param experiment: name of experiment for which to get the list of files
    """

    formate = {'identifier': target['Metabolite name'].strip(" ").replace('[M+HAc-H]','[M+FA-H]').replace('[M+Hac-H]','[M+FA-H]'),
               'accurateMass': target["Average Mz"] - 14.01565,
               'retentionTime': target["Average Rt(min)"],
               'retentionTimeUnit': "minutes",
               'isInternalStandard': target['istd'],
               'requiredForCorrection': False,
               'confirmed': True}
    print('formate: ' + str(formate))
    return formate


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file',
                        help='csv/txt file with the list of targets with headers: '
                             'Metabolite name,Average Mz,Average Rt(min),istd')
    parser.add_argument('-o', '--output', help='name of the yml file to be created')
    parser.add_argument('-s', '--study', help='name of the study', required=True)
    parser.add_argument('-i', '--instrument', help='name of the instrument for the library', default='test')
    parser.add_argument('-c', '--column', help='name of the column for the library', default='test')
    parser.add_argument('--formate', help='calculates the formated adduct from an acetate adduct',
                        dest='formate', default=False, action='store_true')
    parser.add_argument('-m', '--mode', help='ion mode. [\'positive\' or \'negative\']', default='positive',
                        choices=['positive', 'negative'])

    args = parser.parse_args()
    if args.file == '__unknown__' or args.study == "__unknown__":
        parser.print_help()
        SystemExit()

    df = pd.read_csv(args.file, usecols=['Metabolite name', 'Average Mz', 'Average Rt(min)', 'istd'])
    cols = list(df.columns.values)

    targets = []
    for target in df.to_dict(orient='records'):
        if any([x in target['Metabolite name'] for x in ['CSH_posESI', 'CSH posESI', 'CSH_negESI', 'CSH negESI']]):
            target['Metabolite name'] = 'Unknown'

        print('target: ' + str(target))

        t = {'identifier': target['Metabolite name'].strip(" "),
             'accurateMass': target["Average Mz"],
             'retentionTime': target["Average Rt(min)"],
             'retentionTimeUnit': "minutes",
             'isInternalStandard': target['istd'],
             'requiredForCorrection': False,
             'confirmed': True}

        if args.formate and any([adduct in target['Metabolite name'] for adduct in ["[M+HAc-H]-", "[M+Hac-H]-"]]):
            targets.append(calculate_formate(t))
        else:
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
        'minimumPeakIntensity': 5000,
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

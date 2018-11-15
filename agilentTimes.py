import argparse
import glob
import os

import xmltodict
from dateutil import parser as dateparser


def get_timestamps(sources_file):
    # gets the acquisition time from agilent raw data

    file_template = 'AcqData/sample_info.xml'
    timestamps = {}
    with open(sources_file, 'r') as sources:
        # analyze raw data in each source folder

        for source in sources.readlines():
            source = source.strip()
            if not source:
                continue
            print(f'processing files in {source} ')
            os.chdir(source)
            c = 0
            for file in glob.glob('*.d'):
                info_file = f'{source}/{file}/{file_template}'

                with open(info_file, 'r') as rawxml:
                    timestamps[file] = xmltodict.parse(rawxml.read())

                if 0 == c % 50:
                    print('.', end='', flush=True)
                c += 1
            print()

    return timestamps


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output_folder', help='Folder were to save the results.', required=True)
    parser.add_argument('-s', '--raw_data_sources', help='File containing a list of folders where the raw data lives',
                        required=True)

    args = parser.parse_args()

    mzml_root = '/media/luna/luna/mzml'
    sources = args.raw_data_sources
    output = args.output_folder

    timestamps = get_timestamps(sources)

    parsed_times = sorted([(dateparser.parse(name["Value"]), k)
                           for k, v in timestamps.items()
                           for name in v['SampleInfo']['Field'] if name['Name'] == 'AcqTime'
                           ], key=lambda x: x[0])

    if not os.path.isdir(output):
        os.mkdir(output)

    with open(f'{output}/timestamps.txt', 'w') as os:
        for time in parsed_times:
            os.write(f'{time[0]},{time[1]}\n')

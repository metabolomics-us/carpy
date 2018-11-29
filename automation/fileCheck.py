import argparse
import datetime
import glob
import os

import dateutil.parser


def get_missing(fol, need):
    return list(set(n + '.mzml' for n in need) - set(fol))


def clean_processed(file):
    cleaned = []
    print(file)
    with open(file, 'r') as f:
        for line in f.readlines():
            cleaned.append(line.split(' ')[-1])

    print(cleaned)
    return cleaned


def check_converted(mzml_root, study_folder, available):
    converted = os.listdir(mzml_root)
    print('converted files on luna %d' % len(converted))

    not_converted = []
    file_modes = {'positive': [], 'negative': []}

    with open(available, 'r') as rawavail:
        data = rawavail.readlines()

    available_files = [line.split(',')[0].strip().replace('.d', '.mzml') for line in data]

    for mzml_file in available_files:
        if os.path.isfile(f'{mzml_root}/{mzml_file}'):
            if 'pos' in mzml_file.lower():
                file_modes['positive'].append(mzml_file)
            elif 'neg' in mzml_file.lower():
                file_modes['negative'].append(mzml_file)
        else:
            not_converted.append(mzml_file)

    print(f'positive {len(file_modes["positive"])} mode files')
    print(f'negative {len(file_modes["negative"])} mode files')
    print(f'not converted mode files ({len(not_converted)}) : {not_converted} ')

    with open(f'{study_folder}/raw_not_converted.txt', 'w') as conv:
        conv.writelines(map(lambda s: s + '\r', not_converted))

    with open(f'{study_folder}/mzml_positive.txt', 'w') as pos:
        pos.writelines(map(lambda s: s + '\r', file_modes['positive']))

    with open(f'{study_folder}/mzml_negative.txt', 'w') as neg:
        neg.writelines(map(lambda s: s + '\r', file_modes['negative']))

    return 'not_converted.txt', 'mzml_positive.txt', 'mzml_negative.txt'


def check_raw(worklist_files, study_folder, sources_file):
    # compares the provided list of sample names from worklist_files
    # with the actual raw data files on sources_files

    with open(f'{study_folder}/{sources_file}', 'r') as sf:
        sources = [l.strip() for l in sf.readlines() if l.strip()]

    current_directory = os.getcwd()
    raw_files = []
    raw_found = []
    missing_raw_files = set([])
    for list in worklist_files:
        print(f'Checking raw files in {list}')
        with open(f'{study_folder}/{list}', 'r') as fplist:
            files = fplist.readlines()
            c = 0
            for file in files:
                if c % 50 == 0:
                    print("#", end='', flush=True)
                    c = 0
                c += 1

                file = file.strip() if (file.strip().endswith('.d')) else file.strip() + '.d'
                if file == '' or file[0:3] in ['Q:\\', 'R:\\', 'Bat']:
                    continue
                for source in sources:
                    os.chdir(source)
                    found = glob.glob(f'{source}/{file}')

                    if found:
                        raw_files.append(f'{file},{found[0]}')
                        raw_found.append(file)
                        break

                    missing_raw_files.add(file)
            print('')

    os.chdir(current_directory)
    missing_raw_files = set(missing_raw_files) - set(raw_found)
    missing_raw_files = sorted(missing_raw_files)
    print(f'Missing {len(missing_raw_files)} raw files')
    with open(f'{study_folder}/raw_missing.txt', 'w') as notconv:
        notconv.writelines(map(lambda s: s + '\r', missing_raw_files))

    print(f'Found {len(raw_files)} raw files')
    with open(f'{study_folder}/raw_available.csv', 'w') as conv:
        conv.writelines(map(lambda s: s + '\r', raw_files))

    return f'{study_folder}/raw_available.csv', f'{study_folder}/raw_missing.txt'


def check_aws_results():
    newresults = {}
    with open(f'{study_folder}/aws-results.txt', 'r') as nr:
        [newresults.update({k: v}) for k, v in map(lambda l: l.strip().split(','), nr.readlines())]
    reprocessed = [value for (key, value) in sorted(newresults.items()) if
                   dateutil.parser.parse(key) > datetime.datetime(2018, 9, 20, 0, 0, 0)]

    return reprocessed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('files', type=str, help="List of files containing the sample names", default='__unknown__',
                        nargs='+')
    parser.add_argument('-f', '--input_folder', help='Folder were you put the filename list files.', required=True)
    parser.add_argument('-a', '--aws_converted',
                        help='Full path of the file containing all converted samples in AWS (data-carrot)',
                        required=True)
    parser.add_argument('-r', '--aws_results', help='File containing the results from AWS for this study',
                        required=True)
    parser.add_argument('-s', '--raw_data_sources', help='File containing a list of folders where the raw data lives',
                        required=True)
    parser.add_argument('-e', '--raw_data_extension', help='Extension of the raw data files. [.d, .raw]',
                        required=False, default='.d', choices=['.d', '.raw'])

    args = parser.parse_args()
    if args.files == '__unknown__':
        print(parser.print_help())
        SystemExit('Missing file to process')

    mzml_root = '/media/luna/luna/mzml'
    study_folder = args.input_folder
    worklist_files = args.files

    mzml_aws = args.aws_converted
    processed = args.aws_results
    sources = args.raw_data_sources

    available, missing = check_raw(worklist_files, study_folder, sources)

    not_converted, positive, negative = check_converted(mzml_root, study_folder, available)

    reprocessed = set(check_aws_results())

    with open(available) as avail:
        data_avail = set([f.split(',')[0].rstrip('.d') for f in avail.readlines()])

    print(data_avail.__contains__(''), data_avail)
    print(reprocessed.__contains__(''), reprocessed)

    available_list = data_avail - reprocessed
    print(reprocessed - data_avail)
    print(f'available: %d, reprocessed: %d, filtered: %d' % (len(data_avail), len(reprocessed), len(available_list)))
    print(len(available_list), "=", len(data_avail), '-', len(reprocessed), '[', len(data_avail) - len(reprocessed),
          ']')

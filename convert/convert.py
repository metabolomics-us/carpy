#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time

import pandas as pd
import requests
import simplejson as json

apiBase = 'https://api.metabolomics.us/stasis'
common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']


def create_metadata(filename, args):
    data = {'sample': filename,
            'experiment': args.experiment,
            'acquisition': {
                'instrument': args.instrument,
                'method': args.method,
                'ionization': args.ion_mode
            },
            'processing': {
                'method': f'{args.method} | {args.instrument} | {args.column} | {args.ion_mode}'
            },
            'metadata': {
                'class': '',
                'species': args.species,
                'organ': args.organ
            }
            }
    # print(data)

    if args.test:
        status = {'status_code': 200}
    else:
        response = requests.post('%s/acquisition' % apiBase, json=data)
        status = response.status_code
        if status != 200:
            # append line to error file
            print(f'Error adding acquisition data for {filename}')

    print(f'Added acquisition metadata for {filename}')

    return status


def add_tracking(filename, args):
    stat = {}
    handle_ext = {'entered': '', 'acquired': '.d', 'converted': '.mzml'}
    for trk in ['entered', 'acquired', 'converted']:
        if args.test:
            stat[trk] = 200
        else:
            stat[trk] = requests.post('%s/tracking' % apiBase,
                                      json={'status': trk,
                                            'sample': filename,
                                            'fileHandle': filename + handle_ext[trk]}).status_code

        print(f'Added tracking metadata for {filename}', flush=True)

    [print('Error adding tracking \'%s\' for %s' % (stat[trk], filename)) for trk in ['acquired', 'converted'] if
     stat[trk] != 200]

    return stat


def schedule(sample, args):
    data = {'profile': 'carrot.lcms',
            'env': 'prod',
            'sample': f'{sample}.mzml',
            'method': f'{args.method} | {args.instrument} | {args.column} | {args.ion_mode}',
            'task_version': args.task_version
            }

    if (args.test):
        print(data)
        return 200
    else:
        result = requests.post('%s/schedule' % apiBase, json=data)
        if result.status_code != 200:
            print('Error scheduling sample %s' % sample)

        return result.status_code


def fix_sample_filename(sample):
    regex = re.compile(r'\.mzml$|\.d$|\.raw$|\.wiff$|\.cdf$', re.IGNORECASE)

    name = regex.sub('', sample)
    return name


def process(args):
    data = {}
    input = args.file

    if input.endswith('xlsx'):
        data = pd.read_excel(input)
    else:
        data = pd.read_csv(input)

    results = {}

    fargate_max_tasks = 45

    for sheet in data.keys():
        for sample in data[sheet]:
            sample = fix_sample_filename(sample)
            if pd.notna(sample):
                # print('Sample: %s' % sample)
                results[sample] = {}

                if args.acquisition:
                    # add acquisition table generation due to manual processing
                    results[sample]['acquisition'] = json.dumps(create_metadata(sample, args))

                if args.prepare:
                    # add upload to eclipse and convertion to mzml due to manual processing
                    results[sample]['tracking'] = json.dumps(add_tracking(sample, args))

    delay_secs = 300
    for sample in results.keys():
        if args.schedule:
            tasks_count = requests.get('%s/schedule/cluster/count' % apiBase)
            if tasks_count.status_code == 200:
                while int(tasks_count.json()['count']) >= fargate_max_tasks:
                    print(f'Waiting for {delay_secs/60} minutes before scheduling...')
                    time.sleep(delay_secs)
                    tasks_count = requests.get('%s/schedule/cluster/count' % apiBase)

                results[sample]['schedule'] = schedule(sample, args)  # push the sample to the pipeline
                print("scheduled %s - (%d)" % (sample, results[sample]['schedule']))
            else:
                print("Can't get the count of scheduled tasks")

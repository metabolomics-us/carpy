#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import time

import pandas as pd
import requests
import simplejson as json
from requests import RequestException

apiBase = 'https://api.metabolomics.us/stasis'
common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']


def _api_token():
    api_token = os.getenv('PROD_STASIS_API_TOKEN', '').strip()
    if api_token is '':
        raise RequestException("Missing authorization token")

    return {'x-api-key': api_token}


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

    if args.test:
        print(f'{time.strftime("%H:%M:%S")} - {data}')
        status = {'status_code': 200}
    else:
        response = requests.post('%s/acquisition' % apiBase, json=data, headers=_api_token())
        status = response.status_code
        if status != 200:
            # append line to error file
            print(f'{time.strftime("%H:%M:%S")} - Error {status} - {response.text} adding acquisition data for {filename}')

    print(f'{time.strftime("%H:%M:%S")} - Added acquisition metadata for {filename}')

    return status


def add_tracking(filename, args):
    stat = {}
    msg = {}
    handle_ext = {'entered': '', 'acquired': '.d', 'converted': '.mzml'}
    for trk in ['entered', 'acquired', 'converted']:
        data = {'status': trk,
                'sample': filename,
                'fileHandle': filename + handle_ext[trk]}
        if args.test:
            print(f'{time.strftime("%H:%M:%S")} - {data}')
            stat[trk] = 200
        else:
            response = requests.post('%s/tracking' % apiBase, json=data, headers=_api_token())
            stat[trk] = response.status_code
            msg[trk] = json.loads(response.text)

    print(f'{time.strftime("%H:%M:%S")} - Added tracking metadata for {filename}', flush=True)

    [print(f'{time.strftime("%H:%M:%S")} - Error {stat[trk]} - {msg[trk]["message"]} adding tracking for {filename}') for trk in
     ['acquired', 'converted'] if stat[trk] != 200]

    return stat


def schedule(sample, args):
    # TODO: enforce the library override to be the same as the method name to simplify the following check
    profiles = 'carrot.lcms'
    if args.extra_profiles:
        profiles += f',{args.extra_profiles}'

    data = {'profile': profiles,
            'env': 'prod',
            'secure': True,
            'sample': f'{sample}.mzml',
            'method': f'{args.method} | {args.instrument} | {args.column} | {args.ion_mode}',
            'task_version': args.task_version
            }

    if args.test:
        print(f'{time.strftime("%H:%M:%S")} - {data}')
        return 200
    else:
        result = requests.post('%s/secure_schedule' % apiBase, json=data, headers=_api_token())
        if result.status_code != 200:
            print('{time.strftime("%H:%M:%S")} - Error scheduling sample {sample}')

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

    for sample in results.keys():
        if args.schedule:
            results[sample]['schedule'] = schedule(sample, args)  # push the sample to the pipeline
            print(f'{time.strftime("%H:%M:%S")} - Scheduled sample {sample}')
        else:
            print(f'{time.strftime("%H:%M:%S")} - Can\'t get the count of scheduled tasks')

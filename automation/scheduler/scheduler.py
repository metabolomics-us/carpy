#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import re
import time
from abc import ABC
from datetime import datetime

import pandas as pd
import simplejson as json
from stasis_client.client import StasisClient


class Scheduler(ABC):
    def __init__(self, args, stasis: StasisClient):
        pprint.pprint(f'Received configuration: {args}')
        self.config = args
        self.common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']

        if self.config['env'] not in ('prod', 'dev', 'test'):
            self.config['env'] = 'test'

        self.tracking_status = []
        self.acquisition_status = []

        self.stasis = stasis

    def create_metadata(self, filename, chromatography, row, is_retry=False):
        """Adds basic metadata information to stasis.
        Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename
            chromatography: dictionary containing values for method, instrument, column and ion_mode
            row: a line from the input file containing sample, class, specie and organ
            is_retry: indicates if the current call is a retry

        Returns:
            Status code of update. 200 means sample scheduled successfully, error otherwise.
        """

        self.config['experiment']['metadata']['class'] = row['class']
        self.config['experiment']['metadata']['species'] = row['specie'] if pd.notna(row['specie']) else 'unknown'
        self.config['experiment']['metadata']['organ'] = row['organ'] if pd.notna(row['organ']) else 'unknown'

        data = {'sample': filename, 'experiment': str(self.config['experiment']['name']),
                'acquisition': {
                    'instrument': chromatography['instrument'],
                    'method': chromatography['method'],
                    'column': chromatography['column'],
                    'ionisation': chromatography['ion_mode']
                },
                'processing': {
                    'method': f'{chromatography["method"]} | '
                              f'{chromatography["instrument"]} | '
                              f'{chromatography["column"]} | '
                              f'{chromatography["ion_mode"]}'
                },
                'metadata': self.config['experiment']['metadata']}

        status = {}
        if self.config['test']:
            print(f'{time.strftime("%H:%M:%S")} - {data}', flush=True)
            status = {'status_code': 200}
        else:
            try:
                response = self.stasis.sample_acquisition_create(data)
                print(f'{time.strftime("%H:%M:%S")} - Added acquisition metadata for {filename}', flush=True)
                status = response.status_code

            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...', flush=True)
                    time.sleep(5)
                    self.create_metadata(filename, chromatography, row, True)
                else:
                    self.acquisition_status.append(filename)
                    status = 999
            except Exception as e:
                if not is_retry:
                    print(f'Unknown error, retrying in 5 seconds...\n{str(e.args)}', flush=True)
                    time.sleep(5)
                    self.create_metadata(filename, chromatography, row, True)
                else:
                    print(f'unknown error after retrying. Error: {str(e.args)}', flush=True)
                    self.acquisition_status.append(filename)
                    status = 999

        return status

    def add_tracking(self, filename, is_retry=False):
        """Adds sample tracking data to stasis.
         Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename
            is_retry: indicates if the current call is a retry

        Returns:
            Status code for each of the tracking statuses (entered, acquired, converted).
        """
        stat = {}
        handle_ext = {'entered': '', 'acquired': '.d', 'converted': '.mzml'}
        for trk in ['entered', 'acquired', 'converted']:
            data = {'status': trk,
                    'sample': filename,
                    'fileHandle': filename + handle_ext[trk]}
            try:
                if self.config['test']:
                    print(f'{time.strftime("%H:%M:%S")} - {data["sample"]} - {data["status"]} - {data["fileHandle"]}')
                    stat[trk] = 200
                else:
                    response = self.stasis.sample_state_update(data['sample'], data['status'], data['fileHandle'])
                    # response = requests.post('%s/tracking' % self.apiBase, json=data, headers=self.headers())
                    # response.raise_for_status()
                    stat[trk] = response.status_code
            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.add_tracking(filename, True)
                else:
                    self.tracking_status.append(filename)
                    stat[trk] = 999
            except Exception as e:
                if not is_retry:
                    print(f'Unknown error, retrying in 5 seconds...\n{str(e.args)}')
                    time.sleep(5)
                    self.add_tracking(filename, True)
                else:
                    print(f'unknown error after retrying. Error: {str(e.args)}')
                    self.tracking_status.append(filename)
                    stat[trk] = 999

        print(f'{time.strftime("%H:%M:%S")} - Added tracking metadata for {filename}', flush=True)

        return stat

    def fix_sample_filename(self, sample):
        """Removes extension from the sample name

        Args:
            sample: sample name to fix

        Returns:
            Name of the sample without extension
        """
        regex = re.compile(r'\.mzml$|\.d$|\.raw$|\.wiff$|\.cdf$', re.IGNORECASE)

        name = regex.sub('', sample)
        return name

    def process(self, folder):
        """Processes the samples listed in the sample file according to the arguments in args
        Args:
            folder: absolute folder where the experiment definition yaml file is stored.
        Returns:
            Nothing
        """
        data = {}
        input_file = ''
        results = {}

        for chromatography in self.config['experiment']['chromatography']:
            print(f'Preparing chromatographic method: {chromatography["method"]}')
            mode = chromatography['ion_mode']
            results[mode] = {}

            if not chromatography['raw_files_list'] and not chromatography['raw_files']:
                print('processing experiment from folder not implemented yet, sorry.')
            else:
                input_file = chromatography['raw_files_list']

            if input_file.endswith('xlsx'):
                data = pd.read_excel(f'{folder}/{input_file}', usecols=['samples', 'class', 'specie', 'organ'])
            else:
                data = pd.read_csv(f'{folder}/{input_file}', usecols=['samples', 'class', 'specie', 'organ'])

            for i, row in data.iterrows():
                fsample = self.fix_sample_filename(row['samples'])
                if pd.notna(fsample):
                    # print(f'Sample: {fsample}  -- class {cls}')
                    if fsample in results[mode].keys():
                        dupe = f'{fsample}_{time.time()}'
                        print(f'WARNING: Possible duplicate filename: {fsample}, storing as {dupe}')
                    else:
                        dupe = fsample

                    results[mode][dupe] = {}

                    # Acquisition Metadata should happen BEFORE tracking status
                    if self.config['create_acquisition']:
                        # add acquisition table generation due to manual processing
                        results[mode][dupe]['acquisition'] = json.dumps(
                            self.create_metadata(fsample, chromatography, row))

                    # Tracking status should happen AFTER Acquisition table generation
                    if self.config['create_tracking']:
                        # add upload to eclipse and conversion to mzml due to manual processing
                        results[mode][dupe]['tracking'] = json.dumps(self.add_tracking(fsample))

            # self.export_fails(f'missing-trk', self.tracking_status, folder, chromatography)
            # self.export_fails(f'missing-acq', self.acquisition_status, folder, chromatography)

        return results

    def export_fails(self, prefix, data, folder, chromatography):
        curr_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"{folder}/{prefix}-{chromatography['ion_mode'][0:3]}-{curr_time}.txt", "w") as f:
            f.write('samples\n')
            f.write('\n'.join(set(data)))

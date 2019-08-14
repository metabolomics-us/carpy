#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import time
from abc import ABC
from datetime import datetime

import pandas as pd
import requests
import simplejson as json
from requests import Timeout, HTTPError, RequestException


class Scheduler(ABC):
    def __init__(self, args):
        self.args = args
        self.apiBase = 'https://api.metabolomics.us/stasis'
        self.common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']
        self.token_var_name = 'STASIS_API_TOKEN' if self.args.test else 'PROD_STASIS_API_TOKEN'
        self.tracking_status = []
        self.acquisition_status = []
        self.schedule_status = []

    def _api_token(self):
        """Requests an API token

        Returns:
            Authorization token

        Raises:
            RequestException
        """
        api_token = os.getenv(self.token_var_name, '').strip()
        if api_token is '':
            raise RequestException(f"Missing authorization token. Please add a '{self.token_var_name}' environment "
                                   "variable with the correct value")

        return {'x-api-key': api_token}

    def create_metadata(self, filename, is_retry=False):
        """Adds basic metadata information to stasis.
        Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename
            is_retry: indicates if the current call is a retry

        Returns:
            Status code of update. 200 means sample scheduled successfully, error otherwise.
        """
        data = {'sample': filename,
                'experiment': self.args.experiment,
                'acquisition': {
                    'instrument': self.args.instrument,
                    'method': self.args.method,
                    'ionization': self.args.ion_mode
                },
                'processing': {
                    'method': f'{self.args.method} | {self.args.instrument} | {self.args.column} | {self.args.ion_mode}'
                },
                'metadata': {
                    'class': '',
                    'species': self.args.species,
                    'organ': self.args.organ
                }
                }

        status = {}
        if self.args.test:
            print(f'{time.strftime("%H:%M:%S")} - {data}')
            status = {'status_code': 200}
        else:
            try:
                response = requests.post('%s/acquisition' % self.apiBase, json=data, headers=self._api_token())
                response.raise_for_status()
                print(f'{time.strftime("%H:%M:%S")} - Added acquisition metadata for {filename}')
                status = response.status_code

            except Timeout as timeout:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, True)
                else:
                    self.acquisition_status.append(filename)
                    status = timeout.response.status_code

            except HTTPError as ex:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, True)
                else:
                    self.acquisition_status.append(filename)
                    status = ex.response.status_code
            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, True)
                else:
                    self.acquisition_status.append(filename)
                    status = 999
            except Exception as e:
                if not is_retry:
                    print('Unknown error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, True)
                else:
                    print(f'unknown error after retrying. Error: {str(e.args)}')
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
                if self.args.test:
                    print(f'{time.strftime("%H:%M:%S")} - {data}')
                    stat[trk] = 200
                else:
                    response = requests.post('%s/tracking' % self.apiBase, json=data, headers=self._api_token())
                    response.raise_for_status()
                    stat[trk] = response.status_code
            except Timeout as timeout:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.add_tracking(filename, True)
                else:
                    self.tracking_status.append(filename)
                    stat[trk] = timeout.response.status_code
            except HTTPError as ex:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.add_tracking(filename, True)
                else:
                    self.tracking_status.append(filename)
                    stat[trk] = ex.response.status_code
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
                    print('Unknown error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.add_tracking(filename, True)
                else:
                    print(f'unknown error after retrying. Error: {str(e.args)}')
                    self.tracking_status.append(filename)
                    status = 999

        print(f'{time.strftime("%H:%M:%S")} - Added tracking metadata for {filename}', flush=True)

        return stat

    def schedule(self, sample, is_retry=False):
        """Submits a sample for processing

        Args:
            sample: name of the sample
            is_retry: indicates if the current call is a retry

        Returns:
            Status code of scheduling. 200 means sample scheduled successfully, error otherwise.
        """
        # TODO: enforce the library override to be the same as the method name to simplify the following check

        profiles = 'carrot.lcms'
        if self.args.extra_profiles:
            profiles += f',{self.args.extra_profiles}'
        if self.args.msms and 'carrot.targets.dynamic' not in profiles:
            profiles += f', carrot.targets.dynamic'

        data = {'profile': profiles,
                'env': 'test' if self.args.test else 'prod',
                'secure': True,
                'sample': f'{sample}.mzml',
                'method': f'{self.args.method} | {self.args.instrument} | {self.args.column} | {self.args.ion_mode}',
                'task_version': self.args.task_version
                }

        status = ''
        if self.args.test:
            print(f'{time.strftime("%H:%M:%S")} - {data}')
            return 200
        else:
            try:
                result = requests.post('%s/secure_schedule' % self.apiBase, json=data, headers=self._api_token())
                result.raise_for_status()
                print(f'{time.strftime("%H:%M:%S")} - Sample {sample} scheduled.', flush=True)
                status = result.status_code
            except Timeout as timeout:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.schedule(sample, True)
                else:
                    self.schedule_status.append(sample)
                    status = timeout.response.status_code
            except HTTPError as ex:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.schedule(sample, True)
                else:
                    self.schedule_status.append(sample)
                    status = ex.response.status_code
            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.schedule(sample, True)
                else:
                    self.schedule_status.append(sample)
                    status = 999
            except Exception as e:
                if not is_retry:
                    print('Unknown error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.schedule(sample, True)
                else:
                    print(f'unknown error after retrying. Error: {str(e.args)}')
                    self.schedule_status.append(sample)
                    status = 999

            return status

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

    def process(self):
        """Processes the samples listed in the sample file according to the arguments in args
        """
        data = {}
        input_file = self.args.file

        if input_file.endswith('xlsx'):
            data = pd.read_excel(input_file)
        else:
            data = pd.read_csv(input_file)

        results = {}

        for sheet in data.keys():
            for sample in data[sheet]:
                sample = self.fix_sample_filename(sample)
                if pd.notna(sample):
                    # print('Sample: %s' % sample)
                    results[sample] = {}

                    if self.args.prepare:
                        # add upload to eclipse and conversion to mzml due to manual processing
                        results[sample]['tracking'] = json.dumps(self.add_tracking(sample))

                    if self.args.acquisition:
                        # add acquisition table generation due to manual processing
                        results[sample]['acquisition'] = json.dumps(self.create_metadata(sample))

                    if self.args.schedule:
                        # push the sample to the pipeline
                        results[sample]['schedule'] = self.schedule(sample)

        self.export_fails(f'missing-trk', self.tracking_status)
        self.export_fails(f'missing-acq', self.acquisition_status)
        self.export_fails(f'missing-sch', self.schedule_status)

    def export_fails(self, prefix, data):
        base_path = os.path.split(self.args.file)[0]
        curr_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"{base_path}/{prefix}-{self.args.ion_mode[0:3]}-{curr_time}.txt", "w") as f:
            f.write('samples\n')
            f.write('\n'.join(set(data)))

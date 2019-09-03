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
        self.config = args
        self.apiBase = 'https://api.metabolomics.us/stasis'
        self.common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']
        self.token_var_name = 'STASIS_API_TOKEN' if self.config['test'] else 'PROD_STASIS_API_TOKEN'
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
        api_token = os.environ[self.token_var_name].strip()
        if api_token is '':
            raise RequestException(f"Missing authorization token. Please add a '{self.token_var_name}' environment "
                                   "variable with the correct value")

        return {'x-api-key': api_token}

    def create_metadata(self, filename, chromatography, is_retry=False):
        """Adds basic metadata information to stasis.
        Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename
            is_retry: indicates if the current call is a retry

        Returns:
            Status code of update. 200 means sample scheduled successfully, error otherwise.
        """
        data = {'sample': filename, 'experiment': self.config['experiment']['name'], 'acquisition': {
            'instrument': chromatography['instrument'],
            'method': chromatography['method'],
            'ionization': chromatography['ion_mode']
        }, 'processing': {
            'method': f'{chromatography["method"]} | '
                      f'{chromatography["instrument"]} | '
                      f'{chromatography["column"]} | '
                      f'{chromatography["ion_mode"]}'
        }, 'metadata': self.config['experiment']['metadata']}

        status = {}
        if self.config['test']:
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
                    self.create_metadata(filename, chromatography, True)
                else:
                    self.acquisition_status.append(filename)
                    status = timeout.response.status_code

            except HTTPError as ex:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, chromatography, True)
                else:
                    self.acquisition_status.append(filename)
                    status = ex.response.status_code
            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, chromatography, True)
                else:
                    self.acquisition_status.append(filename)
                    status = 999
            except Exception as e:
                if not is_retry:
                    print('Unknown error, retrying in 5 seconds...')
                    time.sleep(5)
                    self.create_metadata(filename, chromatography, True)
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
                if self.config['test']:
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

    def schedule(self, sample, chromatography, is_retry=False):
        """Submits a sample for processing

        Args:
            sample: name of the sample
            is_retry: indicates if the current call is a retry

        Returns:
            Status code of scheduling. 200 means sample scheduled successfully, error otherwise.
        """
        # TODO: enforce the library override to be the same as the method name to simplify the following check

        profiles = 'carrot.lcms'
        if self.config['additional_profiles']:
            profiles += f',{self.config["additional_profiles"]}'
        if self.config['save_msms'] and 'carrot.targets.dynamic' not in profiles:
            profiles += f', carrot.targets.dynamic'

        data = {'profile': profiles,
                'env': 'test' if self.config['test'] else 'prod',
                'secure': True,
                'sample': f'{sample}.mzml',
                'method': f'{chromatography["method"]} | '
                          f'{chromatography["instrument"]} | '
                          f'{chromatography["column"]} | '
                          f'{chromatography["ion_mode"]}',
                'task_version': self.config['task_version']
                }

        status = ''
        if self.config['test']:
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
                    status = self.schedule(sample, chromatography, True)
                else:
                    print(f'Error after retrying to schecule: {str(timeout)}')
                    self.schedule_status.append(sample)
                    status = timeout.response.status_code
            except HTTPError as ex:
                if not is_retry:
                    print('Timeout, retrying in 5 seconds...')
                    time.sleep(5)
                    status = self.schedule(sample, chromatography, True)
                else:
                    print(f'Error after retrying to schecule: {str(ex)}')
                    self.schedule_status.append(sample)
                    status = ex.response.status_code
            except ConnectionError as ce:
                if not is_retry:
                    print('Connection error, retrying in 5 seconds...')
                    time.sleep(5)
                    status = self.schedule(sample, chromatography, True)
                else:
                    self.schedule_status.append(sample)
                    status = 999
            except Exception as e:
                if not is_retry:
                    print('Unknown error, retrying in 5 seconds...')
                    time.sleep(5)
                    status = self.schedule(sample, chromatography, True)
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

    def process(self, folder):
        """Processes the samples listed in the sample file according to the arguments in args
        """
        data = {}
        input_file = ''

        for chromatography in self.config['experiment']['chromatography']:
            if not chromatography['raw_files_list'] or chromatography['raw_files_folder']:
                print('processing experiment from folder not implemented yet, sorry.')
            else:
                input_file = chromatography['raw_files_list']

            if input_file.endswith('xlsx'):
                data = pd.read_excel(f'{folder}/{input_file}')
            else:
                data = pd.read_csv(f'{folder}/{input_file}')

            results = {}

            for sheet in data.keys():
                for sample in data[sheet]:
                    sample = self.fix_sample_filename(sample)
                    if pd.notna(sample):
                        # print('Sample: %s' % sample)
                        results[sample] = {}

                        if self.config['create_tracking']:
                            # add upload to eclipse and conversion to mzml due to manual processing
                            results[sample]['tracking'] = json.dumps(self.add_tracking(sample))

                        if self.config['create_acquisition']:
                            # add acquisition table generation due to manual processing
                            results[sample]['acquisition'] = json.dumps(self.create_metadata(sample, chromatography))

                        if self.config['schedule']:
                            # push the sample to the pipeline
                            results[sample]['schedule'] = self.schedule(sample, chromatography)

            self.export_fails(f'missing-trk', self.tracking_status, folder, chromatography)
            self.export_fails(f'missing-acq', self.acquisition_status, folder, chromatography)
            self.export_fails(f'missing-sch', self.schedule_status, folder, chromatography)

    def export_fails(self, prefix, data, folder, chromatography):
        curr_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"{folder}/{prefix}-{chromatography['ion_mode'][0:3]}-{curr_time}.txt", "w") as f:
            f.write('samples\n')
            f.write('\n'.join(set(data)))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import time
from abc import ABC

import pandas as pd
import requests
import simplejson as json
from requests import RequestException


class Scheduler(ABC):
    def __init__(self, args):
        self.args = args
        self.apiBase = 'https://api.metabolomics.us/stasis'
        self.common_extensions = ['.d', '.mzml', '.raw', '.cdf', '.wiff']
        self.token_var_name = 'STASIS_API_TOKEN' if self.args.test else 'PROD_STASIS_API_TOKEN'

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

    def create_metadata(self, filename):
        """Adds basic metadata information to stasis.
        Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename

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

        if self.args.test:
            print(f'{time.strftime("%H:%M:%S")} - {data}')
            status = {'status_code': 200}
        else:
            response = requests.post('%s/acquisition' % self.apiBase, json=data, headers=self._api_token())
            status = response.status_code
            if status != 200:
                # append line to error file
                print(
                    f'{time.strftime("%H:%M:%S")} - Error {status} - {response.text} adding acquisition data for {filename}')

        print(f'{time.strftime("%H:%M:%S")} - Added acquisition metadata for {filename}')

        return status

    def add_tracking(self, filename):
        """Adds sample tracking data to stasis.
         Use this only for samples handled outside the Acquisition Table Generator

        Args:
            filename: sample filename
            args: conditions of processing

        Returns:
            Status code for each of the tracking statuses (entered, acquired, converted).
        """
        stat = {}
        msg = {}
        handle_ext = {'entered': '', 'acquired': '.d', 'converted': '.mzml'}
        for trk in ['entered', 'acquired', 'converted']:
            data = {'status': trk,
                    'sample': filename,
                    'fileHandle': filename + handle_ext[trk]}
            if self.args.test:
                print(f'{time.strftime("%H:%M:%S")} - {data}')
                stat[trk] = 200
            else:
                response = requests.post('%s/tracking' % self.apiBase, json=data, headers=self._api_token())
                stat[trk] = response.status_code
                msg[trk] = json.loads(response.text)

        print(f'{time.strftime("%H:%M:%S")} - Added tracking metadata for {filename}', flush=True)

        [print(
            f'{time.strftime("%H:%M:%S")} - Error {stat[trk]} - {msg[trk]["message"]} adding tracking for {filename}')
         for trk in
         ['acquired', 'converted'] if stat[trk] != 200]

        return stat

    def schedule(self, sample):
        """Submits a sample for processing

        Args:
            sample: name of the sample
            args: conditions of processing

        Returns:
            Status code of scheduling. 200 means sample scheduled successfully, error otherwise.
        """
        # TODO: enforce the library override to be the same as the method name to simplify the following check
        profiles = 'carrot.lcms'
        if self.args.extra_profiles:
            profiles += f',{self.args.extra_profiles}'

        data = {'profile': profiles,
                'env': 'test' if self.args.test else 'prod',
                'secure': True,
                'sample': f'{sample}.mzml',
                'method': f'{self.args.method} | {self.args.instrument} | {self.args.column} | {self.args.ion_mode}',
                'task_version': self.args.task_version
                }

        if self.args.test:
            print(f'{time.strftime("%H:%M:%S")} - {data}')
            return 200
        else:
            result = requests.post('%s/secure_schedule' % self.apiBase, json=data, headers=self._api_token())
            if result.status_code != 200:
                print('{time.strftime("%H:%M:%S")} - Error scheduling sample {sample}')

            return result.status_code

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
        input = self.args.file

        if input.endswith('xlsx'):
            data = pd.read_excel(input)
        else:
            data = pd.read_csv(input)

        results = {}

        for sheet in data.keys():
            for sample in data[sheet]:
                sample = self.fix_sample_filename(sample)
                if pd.notna(sample):
                    # print('Sample: %s' % sample)
                    results[sample] = {}

                    if self.args.acquisition:
                        # add acquisition table generation due to manual processing
                        results[sample]['acquisition'] = json.dumps(self.create_metadata(sample))

                    if self.args.prepare:
                        # add upload to eclipse and convertion to mzml due to manual processing
                        results[sample]['tracking'] = json.dumps(self.add_tracking(sample))

        for sample in results.keys():
            if self.args.schedule:
                results[sample]['schedule'] = self.schedule(sample)  # push the sample to the pipeline
                print(f'{time.strftime("%H:%M:%S")} - Scheduled sample {sample}')
            else:
                print(f'{time.strftime("%H:%M:%S")} - Can\'t get the count of scheduled tasks\n')
                print(results[sample]['schedule'])

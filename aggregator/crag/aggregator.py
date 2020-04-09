import os
import re
import time
from argparse import Namespace
from typing import Optional, List

import numpy as np
import pandas as pd
import simplejson as json
import tqdm
from stasis_client.client import StasisClient

AVG_BR_ = 'AVG (br)'
RSD_BR_ = '% RSD (br)'
sheet_names = {"intensity": ["Intensity matrix"],
               "mass": ["Mass matrix"],
               "ri": ["Retention index matrix"],
               "rt": ["Original RT matrix"],
               "repl": ["Replaced values"],
               "curve": ["Correction curve"],
               "msms": ["MSMS Spectrum"]}


def percent(x: float, intensity):
    return intensity['found %'] >= x


class NoSamplesFoundException(Exception):
    pass


class Aggregator:

    def __init__(self, args: dict, stasis: Optional[StasisClient] = None, disable_progress_bar=False):
        if isinstance(args, Namespace):
            args = vars(args)

        self.args = args

        if stasis:
            self.stasis_cli = stasis
        else:
            self.stasis_cli = StasisClient()

        self.bucket_used = self.stasis_cli.get_processed_bucket()
        self.disable_progress_bar = disable_progress_bar

    def find_intensity(self, value) -> int:
        """
        Returns the intensity value only for replaced data
        Args:
            value:

        Returns:

        """
        if not value['replaced'] or (value['replaced'] and self.args.get("zero_replacement", False)):
            return round(value['intensity'])
        else:
            return 0

    @staticmethod
    def find_replaced(value) -> int:
        """
        Returns the intensity value only for replaced data
        Args:
            value:

        Returns:

        """
        if value['replaced']:
            return round(value['intensity'])
        else:
            return 0

    @staticmethod
    def add_metadata(samples, data):
        """
        Creates the column headers with sample metadata
        Args:
            samples: list of sample names
            data: dataframe with result data

        Returns: a dataframe with metadata on top of sample results

        """
        dicdata = {'No': None, 'label': None, 'Target RI(s)': None, 'Target mz': None, 'InChIKey':
            ['species', 'organ', 'batch', 'sample_type', 'time'], 'found %': None}
        for sample, idx in zip(samples, range(1, len(samples) + 1)):
            try:
                for d in [t['metadata'] for t in data if t['sample'] == sample]:
                    species = d['metadata']['species']
                    organ = d['metadata']['organ']
                    if '_qc' in sample.lower():
                        sample_type = 'qc'
                    elif '_nist' in sample.lower():
                        sample_type = 'nist'
                    else:
                        sample_type = 'sample'

                    dicdata[sample] = [species, organ, '', sample_type, idx]
            except KeyError as e:
                print('missing sample, {}, {}'.format(idx, sample))  # save sample name to file.
                dicdata[sample] = ['', '', '', '', idx]

        return pd.DataFrame(dicdata)

    def export_excel(self, data, type, infile, sort_index=False):
        """
        Saves a dataframe to excel format
        Args:
            data: the dataframe to export
            type: the name of the excel sheet
            infile: filename of the result to use in excel filename
            sort_index: sort the data on reindexing, True | False

        Returns:

        """

        # saving excel file
        # print(f'{time.strftime("%H:%M:%S")} - Exporting excel file {type}')
        file, ext = os.path.splitext(infile)

        # Build suffix
        if self.args.get("test", False):
            suffix = 'testResults'
        else:
            suffix = 'results'

        if self.args.get("zero_replacement", False):
            suffix += '-repl'
        else:
            suffix += '-norepl'

        seperator = '' if file.endswith("/") else '-'
        output_name = f'{file}{seperator}{type.lower().replace(" ", "_")}-{suffix}.xlsx'

        if type == 'Correction curve':
            data.dropna(inplace=True)
            data.reset_index(drop=True, inplace=True)
            # print(data)

        if sort_index:
            reindexed = data.set_index('No').sort_index()
        else:
            reindexed = data.set_index('No')

        writer = pd.ExcelWriter(output_name)
        reindexed.fillna('').to_excel(writer, type)
        writer.save()

    @staticmethod
    def calculate_average(intensity, mass, rt, origrt, biorecs):
        """
        UNUSED
        Calculates the average intensity, mass and retention index of biorecs

        Argt:
            intensity:
            mass:
            rt:
            origrt:
            biorecs:

        Returns:

        """
        # print(f'{time.strftime("%H:%M:%S")} - Calculating average of biorecs for intensity, '
        #       f'mass and RT (ignoring missing results)')
        np.seterr(invalid='log')

        for i in range(len(intensity)):
            intensity.loc[i, AVG_BR_] = intensity.loc[i, biorecs].mean()
            mass.loc[i, AVG_BR_] = mass.loc[i, biorecs].mean()
            rt.loc[i, AVG_BR_] = rt.loc[i, biorecs].mean()
            origrt.loc[i, AVG_BR_] = 'NA'

    @staticmethod
    def calculate_rsd(intensity, mass, rt, origrt, biorecs):
        """
        UNUSED
        Calculates intensity, mass and retention index Relative Standard Deviation of biorecs
        Args:
            intensity:
            mass:
            rt:
            origrt:
            biorecs:

        Returns:

        """
        # print(f'{time.strftime("%H:%M:%S")} - Calculating %RDS of biorecs for intensity, '
        #       f'mass and RT (ignoring missing results)')
        size = range(len(intensity))
        np.seterr(invalid='log')

        for i in size:
            try:
                intensity.loc[i, RSD_BR_] = (intensity.loc[i, biorecs].std() / intensity.loc[i, biorecs].mean()) * 100
            except Exception as e:
                print(f'{time.strftime("%H:%M:%S")} - Can\'t calculate % RSD for target {intensity.loc[i, "name"]}.'
                      f' Sum of intensities = {intensity.loc[i, biorecs].sum()}')
                pass

            mass.loc[i, RSD_BR_] = (mass.loc[i, biorecs].std() / mass.loc[i, biorecs].mean()) * 100
            rt.loc[i, RSD_BR_] = (rt.loc[i, biorecs].std() / rt.loc[i, biorecs].mean()) * 100
            origrt.loc[i, RSD_BR_] = 'NA'

    def format_sample(self, sample):
        """
        Filters the incoming sample data separating intensity, mass, retention index and replacement values

        Args:
            sample: sample result file

        Returns:

        """
        intensities = []
        masses = []
        rts = []
        origrts = []
        curve = []
        replaced = []
        msms = []

        for k, v in sample['injections'].items():
            intensities = {k: [self.find_intensity(r['annotation']) for r in v['results']]}
            masses = {k: [round(r['annotation']['mass'], 4) for r in v['results']]}
            rts = {k: [round(r['annotation']['retentionIndex'], 2) for r in v['results']]}
            origrts = {k: [round(r['annotation']['nonCorrectedRt'], 2) for r in v['results']]}
            replaced = {k: [self.find_replaced(r['annotation']) for r in v['results']]}
            curve = {k: sample['injections'][k]['correction']['curve']}
            msms = {k: [r['annotation'].get('msms', "") for r in v['results']]}

        return [None, intensities, masses, rts, origrts, curve, replaced, msms]

    @staticmethod
    def build_worksheet(targets, upb, label=' working...', ):
        """
        Structures the data to be 'worksheet' ready
        Args:
            targets: list of targets
            label: progress bar message

        Returns: a dataframe formatted with the first columns of a final report

        """
        rows = []
        pattern = re.compile(".*?_[A-Z]{14}-[A-Z]{10}-[A-Z]")

        i = 1
        bar = tqdm.tqdm(targets, desc=label, unit=' targets', disable=upb)
        for x in bar:
            try:
                rows.append({
                    'No': i,
                    'label': x['name'].rsplit('_', 1)[0],
                    'Target RI(s)': x['retentionTimeInSeconds'],
                    'Target mz': x['mass'],
                    'InChIKey': x['name'].split('_')[-1] if pattern.match(x['name']) else None,
                })
            except TypeError as e:
                bar.write(f'Error adding {x} to the result set. {e.args}')
            finally:
                i = i + 1

        df = pd.DataFrame(rows)  # .set_index('ID')

        return df[['No', 'label', 'Target RI(s)', 'Target mz', 'InChIKey']]

    @staticmethod
    def build_target_identifier(target):
        return f"{target['name']}_{target['retentionTimeInSeconds'] / 60:.1f}_{target['mass']:.1f}"

    def process_sample_list(self, samples, sample_file):
        """
        Runs the aggregation pipeline on the list of samples
        Args:
            samples: list of sample names
            sample_file:

        Returns:

        """
        # use subset of samples for testing
        if self.args.get("test", False):
            samples = samples[:5]

        # creating target list
        results = []

        sbar = tqdm.tqdm(samples, desc='Getting results', unit=' samples', disable=self.disable_progress_bar)
        for sample in sbar:
            sbar.set_description(sample)
            if sample in ['samples']:
                continue

            dir = self.args.get("dir", "/tmp")
            result_file = f'{sample}'
            saved_result = f'{dir}/{result_file}'

            print("looking for {}".format(result_file))
            if self.args.get('save') or not os.path.exists(saved_result):
                print("downloading result data from stasis")
                try:
                    resdata = self.stasis_cli.sample_result_as_json(result_file)
                except Exception as e:
                    resdata = None
            else:
                print("loading existing result data")
                with open(saved_result, 'rb') as data:
                    resdata = json.load(data)
            print("retrieved result data are: '{}'".format(resdata))
            if resdata is None:
                sbar.write(
                    f'Failed getting {sample}. We looked in bucket {self.bucket_used}')
            elif resdata == '':
                sbar.write(
                    f'the result received for {sample} was empty. This is not acceptable!!! Designated local file is {result_file} located at {dir}')
            elif resdata and resdata.get('Error') is None:
                results.append(resdata)
            else:
                raise Exception("this should not have happened!")

        if len(results) == 0:
            raise NoSamplesFoundException("sorry none of your samples were found!")
        targets = self.get_target_list(results)

        # creating spreadsheets
        intensity = self.build_worksheet(targets, upb=self.disable_progress_bar, label='intensity matrix')
        mass = self.build_worksheet(targets, upb=self.disable_progress_bar, label='mass matrix')
        rt = self.build_worksheet(targets, upb=self.disable_progress_bar, label='RI matrix')
        origrt = self.build_worksheet(targets, upb=self.disable_progress_bar, label='RT matrix')
        curve = self.build_worksheet(targets, upb=self.disable_progress_bar, label='curve data')
        replaced = self.build_worksheet(targets, upb=self.disable_progress_bar, label='replacement matrix')
        msms = self.build_worksheet(targets, upb=self.disable_progress_bar, label='MSMS Spectra')

        # populating spreadsheets
        for data in tqdm.tqdm(results, desc='Formatting results', unit=' samples', disable=self.disable_progress_bar):
            sample = data['sample']

            if 'error' not in data:
                formatted = self.format_sample(data)

                intensity[sample] = pd.DataFrame(formatted[1])
                mass[sample] = pd.DataFrame(formatted[2])
                rt[sample] = pd.DataFrame(formatted[3])
                origrt[sample] = pd.DataFrame(formatted[4])
                curve[sample] = pd.DataFrame(formatted[5])
                replaced[sample] = pd.DataFrame(formatted[6])
                msms[sample] = pd.DataFrame(formatted[7])
            else:
                intensity[sample] = np.nan
                mass[sample] = np.nan
                rt[sample] = np.nan
                origrt[sample] = np.nan
                curve[sample] = np.nan
                replaced[sample] = np.nan
                msms[sample] = np.nan

        if not self.args.get('keep_msms'):
            self.filter_msms(msms, intensity)

        # biorecs = [br for br in intensity.columns if 'biorec' in str(br).lower() or 'qc' in str(br).lower()]
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 15)
        pd.set_option('display.width', 1000)

        try:
            discovery = intensity[intensity.columns[5:]].apply(
                lambda row: row.dropna()[row > 0].count() / len(row.dropna()), axis=1)
            intensity.insert(loc=5, column='found %', value=discovery)
        except Exception as e:
            print(f'Error in discovery calculation: {str(e.args)}')

        md = self.add_metadata(samples, results)
        intensity = pd.concat([md, intensity], sort=False).reset_index(drop=True)

        sheet_names['intensity'].append(intensity)
        sheet_names['mass'].append(mass)
        sheet_names['ri'].append(origrt)
        sheet_names['rt'].append(rt)
        sheet_names['repl'].append(replaced)
        sheet_names['curve'].append(curve)
        sheet_names['msms'].append(msms)

        for t in [sheet_names[k] for k in sheet_names.keys()]:
            try:
                self.export_excel(t[1], t[0], sample_file)
            except Exception as exerr:
                print(f'Error creating exel file for {t}')
                print(str(exerr))

    def filter_msms(self, msms, intensity):

        indices = intensity.iloc[:, 5:].idxmax(axis=1)

        reducedMSMS = msms.apply(lambda x: x[indices[x['No'] - 1]], axis=1)
        msms.drop(msms.columns[5:], axis=1, inplace=True)
        msms['MSMS Spectrum'] = reducedMSMS
        return msms

    @staticmethod
    def get_target_list(results):
        """
        Returns the list of targets from a result file
        Args:
            results: result data with target info

        Returns: list of targets
        """

        targets = [x['target'] for x in
                   [results[0]['injections'][k]['results'] for k in list(results[0]['injections'].keys())][0]]

        return targets

    def aggregate(self):
        """
        Collects information on the experiment and decides if aggregation of the full experiment is possible

        Returns: the filename of the aggregated (excel) file
        """

        if "infiles" not in self.args:
            raise KeyError("sorry you need to specify at least one input file for this function")

        for sample_file in self.args["infiles"]:
            if not os.path.isfile(sample_file):
                raise FileNotFoundError("file name {} does not exist".format(sample_file))

            with open(sample_file) as processed_samples:
                samples = [p for p in processed_samples.read().strip().splitlines() if p and p != 'samples']
                self.aggregate_samples(samples, sample_file)

    def aggregate_samples(self, samples: List[str], destination: str = "./"):
        """
        aggegrates the samples at the specifed destination
        :param destination:
        :param samples:
        :return:
        """
        if os.path.exists(destination) is False:
            os.makedirs(destination, exist_ok=True)

        self.process_sample_list(samples, f"{destination}/")

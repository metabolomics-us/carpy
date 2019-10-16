import re

import numpy as np
import pandas as pd
import tqdm

from .stasis import *

AVG_BR_ = 'AVG (br)'
RSD_BR_ = '% RSD (br)'


def percent(x: float, intensity):
    return intensity['found %'] >= x


class Aggregator:

    def __init__(self, args):
        self.args = args

    def find_intensity(self, value) -> int:
        """
        Returns the intensity value only for replaced data
        :param value: the entire annotation object
        :return: intensity value if replaced and requesting replacement values or actual value if not replaced
        """
        if not value['replaced'] or (value['replaced'] and self.args.zero_replacement):
            return round(value["intensity"])
        else:
            return 0

    @staticmethod
    def find_replaced(value) -> int:
        """
        Returns the intensity value only for replaced data
        :param value: the entire annotation object
        :return: intensity value if replaced or 0 if not replaced
        """
        if value['replaced']:
            return round(value["intensity"])
        else:
            return 0

    @staticmethod
    def add_metadata(samples, data):

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
                # print('missing sample, {}, {}'.format(idx, sample)) # save sample name to file.
                dicdata[sample] = ['', '', '', '', idx]

        return pd.DataFrame(dicdata)

    def export_excel(self, intensity, mass, rt, origrt, curve, replaced, infile):

        # saving excel file
        # print(f'{time.strftime("%H:%M:%S")} - Exporting excel file')
        file, ext = os.path.splitext(infile)

        # Build suffix
        if self.args.test:
            suffix = 'testResults'
        else:
            suffix = 'results'

        if self.args.zero_replacement:
            suffix += '-repl'
        else:
            suffix += '-norepl'

        output_name = f'{file}-{suffix}.xlsx'

        intensity = intensity.set_index('No')  # .sort_index()
        mass = mass.set_index('No').sort_index()
        rt = rt.set_index('No').sort_index()
        origrt = origrt.set_index('No').sort_index()
        replaced = replaced.set_index('No').sort_index()

        writer = pd.ExcelWriter(output_name)
        intensity.fillna('').to_excel(writer, 'Intensity matrix')
        mass.fillna('').to_excel(writer, 'Mass matrix')
        rt.fillna('').to_excel(writer, 'Retention index matrix')
        origrt.fillna('').to_excel(writer, 'Original RT matrix')
        replaced.fillna('').to_excel(writer, 'Replaced values')
        curve.fillna('').to_excel(writer, 'Correction curves')
        writer.save()

    @staticmethod
    def calculate_average(intensity, mass, rt, origrt, biorecs):
        """
        Calculates the average intensity, mass and retention index of biorecs
        :param intensity:
        :param mass:
        :param rt:
        :param biorecs:
        :return:
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
        Calculates intensity, mass and retention index Relative Standard Deviation of biorecs
        :param intensity:
        :param mass:
        :param rt:
        :param biorecs:
        :return:
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
            mass.loc[i, RSD_BR_] = (mass.loc[i, biorecs].std() / mass.loc[i, biorecs].mean()) * 100
            rt.loc[i, RSD_BR_] = (rt.loc[i, biorecs].std() / rt.loc[i, biorecs].mean()) * 100
            origrt.loc[i, RSD_BR_] = 'NA'

    def format_sample(self, sample):
        """
        filters the incoming sample data separating intensity, mass, retention index and replacement values
        :param data:
        :return:
        """
        intensities = []
        masses = []
        rts = []
        origrts = []
        curve = []
        replaced = []

        for k, v in sample['injections'].items():

            intensities = {k: [self.find_intensity(r['annotation']) for r in v['results']]}
            masses = {k: [round(r['annotation']['mass'], 4) for r in v['results']]}
            rts = {k: [round(r['annotation']['retentionIndex'], 2) for r in v['results']]}
            origrts = {k: [round(r['annotation']['nonCorrectedRt'], 2) for r in v['results']]}
            curve = {k: v['correction']['curve']}
            replaced = {k: [self.find_replaced(r['annotation']) for r in v['results']]}

        return [None, intensities, masses, rts, origrts, curve, replaced]

    @staticmethod
    def build_worksheet(targets, label=' working...'):
        rows = []
        pattern = re.compile(".*?_[A-Z]{14}-[A-Z]{10}-[A-Z]")

        i = 1
        for x in tqdm.tqdm(targets, desc=label, unit=' targets'):
            rows.append({
                'No': i,
                'label': x['name'].rsplit('_', 1)[0],
                'Target RI(s)': x['retentionTimeInSeconds'],
                'Target mz': x['mass'],
                'InChIKey': x['name'].split('_')[-1] if pattern.match(x['name']) else None,
            })
            i = i + 1

        df = pd.DataFrame(rows)  # .set_index('ID')

        return df[['No', 'label', 'Target RI(s)', 'Target mz', 'InChIKey']]

    def process_sample_list(self, samples, sample_file):
        # use subset of samples for testing
        if self.args.test:
            samples = samples[:5]

        # creating target list
        results = []

        sbar = tqdm.tqdm(samples, desc='Getting results', unit=' samples')
        for sample in sbar:
            sbar.set_description(sample)
            if sample in ['samples']:
                continue

            results.append(get_file_results(sample, self.args.log, self.args.dir, self.args.save))

        targets = self.get_target_list(results)

        # creating spreadsheets
        intensity = self.build_worksheet(targets, 'intensity matrix')
        mass = self.build_worksheet(targets, 'mass matrix')
        rt = self.build_worksheet(targets, 'RI matrix')
        origrt = self.build_worksheet(targets, 'RT matrix')
        curve = self.build_worksheet(targets, 'curve data')
        replaced = self.build_worksheet(targets, 'replacement matrix')

        # populating spreadsheets
        for data in tqdm.tqdm(results, desc='Formatting results', unit=' samples'):
            sample = data['sample']

            if 'error' not in data:
                formatted = self.format_sample(data)

                intensity[sample] = pd.DataFrame(formatted[1])
                mass[sample] = pd.DataFrame(formatted[2])
                rt[sample] = pd.DataFrame(formatted[3])
                origrt[sample] = pd.DataFrame(formatted[4])
                replaced[sample] = pd.DataFrame(formatted[6])

                # curve_data = list(formatted[5].values())[0]
                # curve[sample] = pd.DataFrame(formatted[5], index=formatted[0][: len(curve_data)])
                curve[sample] = pd.DataFrame(formatted[5])
            else:
                intensity[sample] = np.nan
                mass[sample] = np.nan
                rt[sample] = np.nan
                origrt[sample] = np.nan
                replaced[sample] = np.nan

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

        # try:
        #     self.calculate_average(intensity, mass, rt, origrt, biorecs)
        # except Exception as e:
        #     print(f'Error in average calculation: {str(e.args)}')
        # try:
        #     self.calculate_rsd(intensity, mass, rt, origrt, biorecs)
        # except Exception as e:
        #     print(f'Error in average calculation: {str(e.args)}')
        try:
            self.export_excel(intensity, mass, rt, origrt, curve, replaced, sample_file)
        except Exception as e:
            print(f'Error in excel export: {str(e.args)}')

    @staticmethod
    def get_target_list(results):
        k = list(results[0]['injections'].keys())[0]

        targets = [x['target'] for x in results[0]['injections'][k]['results']]

        return targets

    def aggregate(self):
        """
        Collects information on the experiment and decides if aggregation of the full experiment is possible

        :param args: parameters containing the experiment name
        :return: the filename of the aggregated (excel) file
        """

        for sample_file in self.args.infiles:
            if not os.path.isfile(sample_file):
                print(f'Can\'t find the file {sample_file}')
                exit(-1)

            with open(sample_file) as processed_samples:
                samples = [p for p in processed_samples.read().strip().splitlines() if p and p != 'samples']
                self.process_sample_list(samples, sample_file)

import os
import re
import time

import numpy as np
import pandas as pd
import requests
import simplejson as json

from .stasis import *


AVG_BR_ = 'AVG (br)'
RSD_BR_ = '% RSD (br)'


class Aggregator:

    def __init__(self, args):
        self.count = 0
        self.args = args


    def find_replaced(self, value) -> int:
        """
        Returns the intensity value only for replaced data
        :param value: the entire annotation object
        :return: intensity value if replaced or 0 if not replaced
        """
        if value['replaced']:
            return round(value["intensity"])
        else:
            return 0


    def add_header(self, dest, data):
        species = data['metadata']['species']
        organ = data['metadata']['organ']
        method = data['acquisition']['method']
        instrument = data['acquisition']['instrument']
        ion_mode = data['acquisition']['ionization']
        sample = dest.iterkeys().next()

        new_data = [sample, species, organ, method, instrument, ion_mode, ''].append(dest.get(sample))

        print(f'updated: {new_data}')
        return new_data


    def export_excel(self, intensity, mass, rt, origrt, curve, replaced, infile, test):
        # saving excel file
        print(f'{time.strftime("%H:%M:%S")} - Exporting excel file')
        file, ext = os.path.splitext(infile)
        output_name = f'{file}_results.xlsx'

        if test:
            output_name = f'{file}_testResults.xlsx'

        intensity.set_index('Target name')
        mass.set_index('Target name')
        rt.set_index('Target name')
        origrt.set_index('Target name')
        replaced.set_index('Target name')

        writer = pd.ExcelWriter(output_name)
        intensity.fillna('').to_excel(writer, 'Intensity matrix')
        mass.fillna('').to_excel(writer, 'Mass matrix')
        rt.fillna('').to_excel(writer, 'Retention index matrix')
        origrt.fillna('').to_excel(writer, 'Original RT matrix')
        replaced.fillna('').to_excel(writer, 'Replaced values')
        curve.fillna('').to_excel(writer, 'Correction curves')
        writer.save()


    def calculate_average(self, intensity, mass, rt, origrt, biorecs):
        """
        Calculates the average intensity, mass and retention index of biorecs
        :param intensity:
        :param mass:
        :param rt:
        :param biorecs:
        :return:
        """
        print(f'{time.strftime("%H:%M:%S")} - Calculating average of biorecs for intensity, mass and RT (ignoring missing '
              f'results)')
        np.seterr(invalid='log')

        for i in range(len(intensity)):
            intensity.loc[i, AVG_BR_] = intensity.loc[i, biorecs].mean()
            mass.loc[i, AVG_BR_] = mass.loc[i, biorecs].mean()
            rt.loc[i, AVG_BR_] = rt.loc[i, biorecs].mean()
            origrt.loc[i, AVG_BR_] = 'NA'


    def calculate_rsd(self, intensity, mass, rt, origrt, biorecs):
        """
        Calculates intensity, mass and retention index Relative Standard Deviation of biorecs
        :param intensity:
        :param mass:
        :param rt:
        :param biorecs:
        :return:
        """
        print(f'{time.strftime("%H:%M:%S")} - Calculating %RDS of biorecs for intensity, mass and RT (ignoring missing '
              f'results)')
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

        dupes = {}

        for k, v in sample['injections'].items():
            for x in v['results']:
                if x['target']['id'] not in dupes:
                    dupes[x['target']['id']] = x
                else:
                    i = x['target']['id']
                    print(f"{i}: ({x['target']['name']}, {x['target']['mass']}, {x['target']['retentionIndex']}) -> ({dupes[i]['target']['name']}, {dupes[i]['target']['mass']}, {dupes[i]['target']['retentionIndex']})")

            ids = [r['target']['id'] for r in v['results']]
            intensities = {k: [round(r['annotation']['intensity']) for r in v['results']]}
            masses = {k: [round(r['annotation']['mass'], 4) for r in v['results']]}
            rts = {k: [round(r['annotation']['retentionIndex'], 2) for r in v['results']]}
            origrts = {k: [round(r['annotation']['nonCorrectedRt'], 2) for r in v['results']]}
            curve = {k: v['correction']['curve']}
            replaced = {k: [self.find_replaced(r['annotation']) for r in v['results']]}

        return [ids, intensities, masses, rts, origrts, curve, replaced]


    def build_worksheet(self, targets):
        rows = []
        pattern = re.compile(".*?_[A-Z]{14}-[A-Z]{10}-[A-Z]")

        for x in targets:
            rows.append({
                'ID': x['id'],
                'Target name': x['name'].rsplit('_', 1)[0],
                'Target RI(s)': x['retentionIndex'],
                'Target mz': x['mass'],
                'Target RI(s)': x['retentionIndex'],
                'InChIKey': x['name'].split('_')[-1] if pattern.match(x['name']) else None,
            })

        df = pd.DataFrame(rows)
        df[AVG_BR_] = np.nan
        df[RSD_BR_] = np.nan

        return df[['Target name', 'Target RI(s)', 'Target mz', 'InChIKey', AVG_BR_, RSD_BR_]]


    def build_target_list(self, targets, sample, intensity_filter=0):
        startIndex = 0
        new_targets = []

        # Lookup for target names    
        target_names = {x['name']: x['id'] for x in targets if x['name'] != 'Unknown'}

        # Get all annotations and sort by mass
        annotations = sum([v['results'] for v in sample['injections'].values()], [])
        annotations.sort(key=lambda x: x['target']['mass'])

        max_intensity = max(x['annotation']['intensity'] for x in annotations)

        # Match all targets in sample data to master target list 
        for x in annotations:
            if x['target']['name'] in target_names:
                x['target']['id'] = target_names[x['target']['name']]
                continue

            matched = False
            ri = x['target']['retentionIndex']

            for i in range(startIndex, len(targets)):
                if targets[i]['mass'] < x['target']['mass'] - self.args.mz_tolerance:
                    startIndex = i + 1
                    continue
                if targets[i]['mass'] > x['target']['mass'] + self.args.mz_tolerance:
                    break

                if ri - self.args.rt_tolerance <= targets[i]['retentionIndex'] <= ri + self.args.rt_tolerance:
                    print(f"Matched unknown ({ri}, {x['target']['mass']}) -> ({targets[i]['id']}, {targets[i]['name']}, {targets[i]['retentionIndex']}, {targets[i]['mass']})")
                    x['target']['id'] = targets[i]['id']
                    break

            if not matched and x['annotation']['intensity'] >= intensity_filter * max_intensity:
                t = x['target']
                t['id'] = len(targets) + len(new_targets) + 1
                new_targets.append(t)
            else:
                print(f"Skipped feature ({x['target']['name']}, {ri}, {x['target']['mass']}), less than {intensity_filter * 100}% base peak intensity")

        return sorted(targets + new_targets, key=lambda x: x['mass'])


    def process_sample_list(self, sample_file):
        if not os.path.isfile(sample_file):
            print(f'Can\'t find the file {sample_file}')
            exit(-1)

        with open(sample_file) as processed_samples:
            samples = [p for p in processed_samples.read().strip().splitlines() if p]

        # use subset of samples for testing
        if self.args.test:
            samples = samples[:3]

        # creating target list
        results = []
        targets = []

        for sample in samples:
            if sample in ['samples']:
                continue

            data = get_file_results(sample, False, self.count, self.args.dir, self.args.save)
            self.count += 1

            results.append(data)
            targets = self.build_target_list(targets, data)

        # creating spreadsheets
        intensity = self.build_worksheet(targets)
        mass = self.build_worksheet(targets)
        rt = self.build_worksheet(targets)
        origrt = self.build_worksheet(targets)
        curve = self.build_worksheet(targets)
        replaced = self.build_worksheet(targets)

        # populating spreadsheets
        for data in results:
            if 'error' not in data:
                formatted = self.format_sample(data)

                print(len(formatted[0]), len(set(formatted[0])))

                intensity[sample] = pd.DataFrame(formatted[1], index=formatted[0])
                mass[sample] = pd.DataFrame(formatted[2], index=formatted[0])
                rt[sample] = pd.DataFrame(formatted[3], index=formatted[0])
                origrt[sample] = pd.DataFrame(formatted[4], index=formatted[0])
                replaced[sample] = pd.DataFrame(formatted[6], index=formatted[0])

                curve_data = list(formatted[5].values())[0]
                curve[sample] = pd.DataFrame(formatted[5], index=formatted[0][: len(curve_data)])
            else:
                intensity[sample] = np.nan
                mass[sample] = np.nan
                rt[sample] = np.nan
                origrt[sample] = np.nan
                replaced[sample] = np.nan

        biorecs = [br for br in intensity.columns if 'biorec' in str(br).lower() or 'qc' in str(br).lower()]
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.width', 1000)

        try:
            self.calculate_average(intensity, mass, rt, origrt, biorecs)
        except Exception as e:
            print(f'Error in average calculation: {str(e.args)}')
        try:
            self.calculate_rsd(intensity, mass, rt, origrt, biorecs)
        except Exception as e:
            print(f'Error in average calculation: {str(e.args)}')
        try:
            self.export_excel(intensity, mass, rt, origrt, curve, replaced, sample_file, self.args.test)
        except Exception as e:
            print(f'Error in excel export: {str(e.args)}')


    def aggregate(self):
        """
        Collects information on the experiment and decides if aggregation of the full experiment is possible

        :param args: parameters containing the experiment name
        :return: the filename of the aggregated (excel) file
        """

        # commented since it returns partial list of experiment files
        # print(f"Aggregating results for experiment '{args.experiment}'")
        # files = getExperimentFiles(args.experiment)
        # print(files)

        for file in self.args.infiles:
            self.process_sample_list(file)


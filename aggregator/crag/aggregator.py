import re

import numpy as np
import pandas as pd
import tqdm

from .stasis import *

AVG_BR_ = 'AVG (br)'
RSD_BR_ = '% RSD (br)'
sheet_names = {"intensity": "Intensity matrix",
               "mass": "Mass matrix",
               "ri": "Retention index matrix",
               "rt": "Original RT matrix",
               "repl": "Replaced values",
               "curve": "Correction curve"}


def percent(x: float, intensity):
    return intensity['found %'] >= x


class Aggregator:

    def __init__(self, args):
        self.args = args

    def find_intensity(self, value) -> int:
        """
        Returns the intensity value only for replaced data
        Args:
            value:

        Returns:

        """
        if not value['replaced'] or (value['replaced'] and self.args.zero_replacement):
            return round(value["intensity"])
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
            return round(value["intensity"])
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
                # print('missing sample, {}, {}'.format(idx, sample)) # save sample name to file.
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
        if self.args.test:
            suffix = 'testResults'
        else:
            suffix = 'results'

        if self.args.zero_replacement:
            suffix += '-repl'
        else:
            suffix += '-norepl'

        output_name = f'{type.lower().replace(" ", "_")}-{file}-{suffix}.xlsx'

        if type == 'Correction curve':
            data.drop(columns=['label', 'Target RI(s)', 'Target mz', 'InChIKey'], inplace=True)
            data.dropna(inplace=True)
            data.reset_index(drop=True, inplace=True)
            print(data)


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

        Args:
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
                # print(f'{time.strftime("%H:%M:%S")} - Can\'t calculate % RSD for target {intensity.loc[i, "name"]}.'
                #       f' Sum of intensities = {intensity.loc[i, biorecs].sum()}')
                pass

            mass.loc[i, RSD_BR_] = (mass.loc[i, biorecs].std() / mass.loc[i, biorecs].mean()) * 100
            rt.loc[i, RSD_BR_] = (rt.loc[i, biorecs].std() / rt.loc[i, biorecs].mean()) * 100
            origrt.loc[i, RSD_BR_] = 'NA'

    def format_sample(self, sample):
        """
        Filters the incoming sample data separating intensity, mass, retention index and replacement values

        Args:
            sample: result file

        Returns:

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
            replaced = {k: [self.find_replaced(r['annotation']) for r in v['results']]}
            curve = {k: sample['injections'][k]['correction']['curve']}


        return [None, intensities, masses, rts, origrts, curve, replaced]

    @staticmethod
    def build_worksheet(targets, label=' working...'):
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
        for x in tqdm.tqdm(targets, desc=label, unit=' targets'):
            try:
                rows.append({
                    'No': i,
                    'label': x['name'].rsplit('_', 1)[0],
                    'Target RI(s)': x['retentionTimeInSeconds'],
                    'Target mz': x['mass'],
                    'InChIKey': x['name'].split('_')[-1] if pattern.match(x['name']) else None,
                })
            except TypeError as e:
                print(f'Error adding {x} to the result set. {e.args}')
            finally:
                i = i + 1

        df = pd.DataFrame(rows)  # .set_index('ID')

        return df[['No', 'label', 'Target RI(s)', 'Target mz', 'InChIKey']]

    @staticmethod
    def build_target_identifier(target):
        return f"{target['name']}_{target['retentionTimeInSeconds'] / 60:.1f}_{target['mass']:.1f}"

    # DEPRECATED, it returns a different number of targets compared to the library
    # def build_target_list(self, targets, sample, intensity_filter=0):
    #     """Creates a list of unique targets from the list of sample results
    #     Params
    #         targets: list of 'target' dicts {'id': '', 'name': '', 'mass': 0.0, 'retentionTimeInSeconds': 0.0}
    #         sample: result data in json format
    #         intensity_filter: consider masses with intensity above this value. Default=0
    #     Returns
    #         A list of unique 'target' dicts.
    #     """
    #     if 'error' in sample:
    #         if self.args.log:
    #             print('Error:', sample)
    #         return targets
    #
    #     start_index = 0
    #     new_targets = []
    #
    #     # Lookup for target names
    #     # Commented version for future when target RT m/z has been corrected
    #     # target_lookup = {self.build_target_identifier(x): x['id'] for x in targets if x['name'] != 'Unknown'}
    #     target_lookup = {x['name']: x['id'] for x in targets if x['name'] != 'Unknown'}
    #
    #     # Get all annotations and sort by mass
    #     annotations = sum([v['results'] for v in sample['injections'].values()], [])
    #     annotations.sort(key=lambda x: x['target']['mass'])
    #
    #     max_intensity = max(x['annotation']['intensity'] for x in annotations)
    #
    #     # Avoid duplicate targets
    #     observed_targets = set()
    #
    #     # Match all targets in sample data to master target list
    #     for x in annotations:
    #         # For now, horrible hack to handle duplicate targets
    #         if x['target']['name'] != 'Unknown':
    #             if x['target']['name'] in observed_targets:
    #                 continue
    #             observed_targets.add(x['target']['name'])
    #
    #         # target_identifier = self.build_target_identifier(x['target'])
    #         target_identifier = x['target']['name']
    #
    #         if target_identifier in target_lookup:
    #             x['target']['id'] = target_lookup[target_identifier]
    #             continue
    #
    #         matched = False
    #         ri = x['target']['retentionTimeInSeconds']
    #
    #         for i in range(start_index, len(targets)):
    #             if targets[i]['mass'] < x['target']['mass'] - self.args.mz_tolerance:
    #                 start_index = i + 1
    #                 continue
    #             if targets[i]['mass'] > x['target']['mass'] + self.args.mz_tolerance:
    #                 break
    #
    #             if ri - self.args.rt_tolerance <= targets[i]['retentionTimeInSeconds'] <= ri + self.args.rt_tolerance:
    #                 if self.args.log:
    #                     print(f"Matched ({x['target']['name']}, {ri}, {x['target']['mass']}) -> ({targets[i]['id']},"
    #                           f"{targets[i]['name']}, {targets[i]['retentionTimeInSeconds']}, {targets[i]['mass']})")
    #
    #                 x['target']['id'] = targets[i]['id']
    #                 matched = True
    #                 break
    #
    #         if not matched:
    #             if x['annotation']['intensity'] >= intensity_filter * max_intensity:
    #                 t = x['target']
    #                 t['id'] = len(targets) + len(new_targets) + 1
    #                 new_targets.append(t)
    #             else:
    #                 if self.args.log:
    #                     print(f"Skipped feature ({x['target']['name']}, {ri}, {x['target']['mass']}, "
    #                           f"{x['annotation']['intensity']}), "
    #                           f"less than {intensity_filter * 100}% base peak intensity")
    #
    #     return sorted(targets + new_targets, key=lambda x: x['mass'])

    def process_sample_list(self, samples, sample_file):
        """
        Runs the aggregation pipeline on the list of samples
        Args:
            samples: list of sample names
            sample_file: input file with list of samples

        Returns:

        """
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

        for t in [sheet_names[k] for k in sheet_names.keys()]:
            try:
                self.export_excel(intensity, t, sample_file)
            except Exception as exerr:
                print(f'Error creating exel file for {t}')
                print(exerr.args)

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

        for sample_file in self.args.infiles:
            if not os.path.isfile(sample_file):
                print(f'Can\'t find the file {sample_file}')
                exit(-1)

            with open(sample_file) as processed_samples:
                samples = [p for p in processed_samples.read().strip().splitlines() if p and p != 'samples']
                self.process_sample_list(samples, sample_file)

import re
import os

from pandas import ExcelWriter
from tqdm import tqdm
import pandas as pd
from abc import ABC


class Merger(ABC):

    @staticmethod
    def load_file(filename):
        print('loading report...', flush=True)
        return pd.read_excel(filename)

    def merge_file(self, filename):
        data = Merger.load_file(filename)
        return self.merge(data)

    def merge(self, data):
        print('merging reinjection data...', flush=True)
        clean = data.copy()
        reinj = self.calculate_reinjection_map(data)

        bar = tqdm(reinj.keys())
        for x in bar:
            try:
                bar.update()
                if x not in clean.columns:
                    bar.write(f'renaming {reinj.get(x)[-1]} to {x}')
                    clean.rename(columns={reinj.get(x)[-1]: x}, inplace=True)
                else:
                    bar.write(f'replacing {x} with {reinj.get(x)[-1]}')
                    clean[x] = clean[reinj.get(x)[-1]]

                try:
                    [clean.drop(y, inplace=True, axis=1) for y in reinj.get(x)]
                except KeyError:
                    pass    # not found since it was renamed
            except KeyError as ke:
                bar.write(f'error finding clean[{x}]')

        bar.close()

        return clean

    def calculate_reinjection_map(self, data):
        regex = re.compile('^(.*_(?:Pos|Neg|ReRun)_[a-z0-9A-Z]{5})_.+$')

        reinj = list(filter(regex.search, data.columns))
        reinjections = {regex.search(s).group(1): [t for t in reinj if t.startswith(regex.search(s).group(1))] for s in reinj}

        return reinjections

    @staticmethod
    def save_report(data, filename):
        fpath, fname = os.path.split(filename)
        output = f'{fpath}/merged-{fname}'
        print(f'saving report {output}')

        try:
            with ExcelWriter(f'{output}') as writer:
                data.to_excel(writer)
        except Exception as ex:
            print(f'error saving excel report - {str(ex)}')
            return False

        return True

from unittest import TestCase

from merger.Merger import Merger


class MergerTests(TestCase):
    filename = "results.xlsx"
    data = None

    def setup_class(self):
        self.merger = Merger()
        self.data = Merger.load_file(self.filename)

    def test_load_file(self):
        print(f'columns: {self.data.columns}')
        print(f'shape (rows, columns): {self.data.shape}')
        self.assertIsNotNone(self.data, "load_file didn't return data")

    def test_calculate_reinjection_map(self):
        reinjections = self.merger.calculate_reinjection_map(self.data)

        self.assertEqual(142, len(reinjections.items()))

    def test_merge(self):
        cleaned = self.merger.merge(self.data)
        reinjmap = self.merger.calculate_reinjection_map(self.data)
        revdiff = len(list(set(cleaned.columns) - set(self.data.columns)))

        tmp = {k: len(v) for k, v in reinjmap.items()}
        count = sum(v for v in tmp.values()) - revdiff

        print(f'dirty cols: {len(self.data.columns)}')
        print(f'clean cols: {len(cleaned.columns)}')
        print(f'new in clean: {revdiff}')

        self.assertGreater(len(self.data.columns), len(cleaned.columns))
        self.assertEqual(len(self.data.columns)-count, len(cleaned.columns))

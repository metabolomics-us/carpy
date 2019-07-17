import unittest

from crag import stasis


class TestStasis(unittest.TestCase):
    def test_getfile_results(self):
        sample = 'B12A_TeddyLipids_Pos_QC001'
        response = stasis.get_file_results(sample, False)
        self.assertNotIn('error', response)
        self.assertEqual(sample, response['sample'])

    def test_get_invalid_file_results(self):
        response = stasis.get_file_results('invalid', False)

        self.assertIn('error', response)
        self.assertIn('sample', response)
        self.assertIn('injections', response)

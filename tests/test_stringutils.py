#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from eatb.utils.stringutils import whitespace_separated_text_to_dict


class TestStringUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_whitespace_separated_text_to_dict(self):
        input_text_map = """
        IP.AVID.RA.18005.rep0.seg0 4294e5eb-6d95-4b31-b544-53eb50711a56
        IP.AVID.RA.18005.rep1.seg1 d9bb0f20-aa8d-43b8-95ca-9bfcb23da832
        """
        expected_result_map = {
            'IP.AVID.RA.18005.rep0.seg0': '4294e5eb-6d95-4b31-b544-53eb50711a56',
            'IP.AVID.RA.18005.rep1.seg1': 'd9bb0f20-aa8d-43b8-95ca-9bfcb23da832',
        }
        result_map = whitespace_separated_text_to_dict(input_text_map)
        print(result_map)
        self.assertEqual(2, len(result_map), "Incorrect size of result map")
        self.assertEqual('4294e5eb-6d95-4b31-b544-53eb50711a56', expected_result_map.pop('IP.AVID.RA.18005.rep0.seg0'))
        self.assertEqual('d9bb0f20-aa8d-43b8-95ca-9bfcb23da832', expected_result_map.pop('IP.AVID.RA.18005.rep1.seg1'))

    def test_whitespace_in_package_name(self):
        input_text_map = """
        HU_MNL_OL_XX - IDfd20a7fe-ab32-4bdb-ba7c-b10d9449025a    urn:uuid:8e231c2d-ad35-b73f-5923-f0d9aa8a9e24
        HU_MNL_OL_XX - ID1ac7249b-9e16-4d27-a0fc-0d8459e5066b    urn:uuid:5dae14ae-00aa-6ecc-3008-0e8ac2e692c4
        """
        expected_result_map = {
            'HU_MNL_OL_XX - IDfd20a7fe-ab32-4bdb-ba7c-b10d9449025a': 'urn:uuid:8e231c2d-ad35-b73f-5923-f0d9aa8a9e24',
            'HU_MNL_OL_XX - ID1ac7249b-9e16-4d27-a0fc-0d8459e5066b': 'urn:uuid:5dae14ae-00aa-6ecc-3008-0e8ac2e692c4',
        }
        result_map = whitespace_separated_text_to_dict(input_text_map)
        self.assertEqual(2, len(result_map), "Incorrect size of result map")
        self.assertEqual('urn:uuid:8e231c2d-ad35-b73f-5923-f0d9aa8a9e24', expected_result_map.pop('HU_MNL_OL_XX - IDfd20a7fe-ab32-4bdb-ba7c-b10d9449025a'))
        self.assertEqual('urn:uuid:5dae14ae-00aa-6ecc-3008-0e8ac2e692c4', expected_result_map.pop('HU_MNL_OL_XX - ID1ac7249b-9e16-4d27-a0fc-0d8459e5066b'))

    def test_tab_whitespace_separated_text_to_dict(self):
        input_text_map = """
        IP.AVID.RA.18005.rep0.seg0  \t 4294e5eb-6d95-4b31-b544-53eb50711a56
        """
        expected_result_map = {
            'IP.AVID.RA.18005.rep0.seg0': '4294e5eb-6d95-4b31-b544-53eb50711a56',
        }
        result_map = whitespace_separated_text_to_dict(input_text_map)
        self.assertEqual(1, len(result_map), "Incorrect size of result map")
        self.assertEqual('4294e5eb-6d95-4b31-b544-53eb50711a56', expected_result_map.pop('IP.AVID.RA.18005.rep0.seg0'))


if __name__ == '__main__':
    unittest.main()

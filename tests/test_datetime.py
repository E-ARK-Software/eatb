#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from eatb import ROOT

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa: E402
import unittest

from eatb.utils.datetime import get_file_ctime_iso_date_str, current_timestamp, LengthBasedDateFormat, \
    DT_ISO_FORMAT, ts_date, date_format, current_date


class TestDateTime(unittest.TestCase):

    test_file = os.path.join(ROOT, 'tests/test_resources/test.txt')

    def test_file_ctime_iso_date_str(self):
        """
         Checksum (type MD5) must return SHA256 checksum value
        """

        self.assertEqual(20, len(get_file_ctime_iso_date_str(TestDateTime.test_file)))
        self.assertEqual(19, len(get_file_ctime_iso_date_str(TestDateTime.test_file, "%d.%m.%Y %H:%M:%S")))

    def test_current_timestamp(self):
        self.assertEqual(19, len(current_timestamp()))

    def test_length_based_format(self):
        lbf = LengthBasedDateFormat("2019")
        self.assertEqual("2019-01-01T00:00:00Z", lbf.format(DT_ISO_FORMAT, 4))

    def test_ts_date(self):
        self.assertEqual(19, len(ts_date()))

    def test_date_format(self):
        self.assertEqual(20, len(date_format(current_date())))


if __name__ == '__main__':
    unittest.main()

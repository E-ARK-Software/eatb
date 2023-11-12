#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tarfile
import unittest

from eatb import ROOT
from eatb.packaging import ChunkedTarEntryReader


class ChunkedTarEntryReaderTest(unittest.TestCase):

    tar_test_file = None
    entry = None
    tfile = None

    @classmethod
    def setUpClass(cls):
        ChunkedTarEntryReaderTest.tar_test_file = os.path.join(ROOT, "tests/test_resources/storage-test/xyz.tar")
        ChunkedTarEntryReaderTest.entry = "xyz/representations/default/data/example.txt"
        ChunkedTarEntryReaderTest.tfile = tarfile.open(ChunkedTarEntryReaderTest.tar_test_file, 'r')

    def test_default_chunk_size(self):
        cter1 = ChunkedTarEntryReader(ChunkedTarEntryReaderTest.tfile)
        self.assertEqual(1, sum([1 for _ in cter1.chunks(ChunkedTarEntryReaderTest.entry)]))
        ChunkedTarEntryReader(ChunkedTarEntryReaderTest.tfile)

    def test_custom_chunk_size(self):
        cter2 = ChunkedTarEntryReader(ChunkedTarEntryReaderTest.tfile, 8192)
        self.assertEqual(1, sum([1 for _ in cter2.chunks(ChunkedTarEntryReaderTest.entry)]))
        ChunkedTarEntryReader(ChunkedTarEntryReaderTest.tfile)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tarfile

from eatb.utils.reporters import default_reporter

class ChunkedTarEntryReader(object):
    """
    Chunked TAR entry reader allowing to read large TAR entries.
    """

    def __init__(self, tfile: tarfile, chunksize: int = 512):
        self.tfile = tfile
        self.chunksize = chunksize
        self.bytesread = 0

    def close(self):
        if self.tfile:
            return self.tfile.close()
        return True

    def chunks(self, entry, total_bytes_read=0, bytes_total=-1):
        """
        Chunk generator, returns data chunks which can be iterated in a for loop.
        :return: generator with data chunks
        """
        tinfo = self.tfile.getmember(entry)

        if bytes_total == -1:
            bytes_total = tinfo.size
        f = self.tfile.extractfile(tinfo)

        def readchunk():
            return f.read(self.chunksize)

        for chunk in iter(readchunk, ''):
            self.bytesread += len(chunk)
            percent = (total_bytes_read+self.bytesread) * 100 / bytes_total
            default_reporter(percent)
            yield chunk
            if percent == 100:
                break

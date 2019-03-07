#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))  # noqa: E402
try:
    from fido.fido import Fido
    fido_disabled = False
except ImportError:
    fido_disabled = True


class FormatIdentification():
    """
    File Format Identification
    """

    def __init__(self):
        if not fido_disabled:
            self.fid = Fido()
            self.fid.handle_matches = self.print_matches
            self.lastFmt = None

    def identify_file(self, entry):
        """
        This function identifies the file format of every file that is handed over.
        """
        assert not fido_disabled, "Fido module is not available!"
        self.fid.identify_file(entry)
        return self.lastFmt

    def get_mime_for_puid(self, puid):
        """

        :param puid: PRONOM Persistent Unique Identifier
        :return: mime type string (default: application/octet-stream)
        """
        assert not fido_disabled, "Fido module is not available!"
        mime_tag = "mime"
        fmtres = self.fid.puid_format_map[puid]
        childs = [child for child in fmtres if child.tag.endswith(mime_tag)]
        if len(childs) == 1:
            return (childs[0]).text.strip()
        else:
            return "application/octet-stream"

    def print_matches(self, fullname, matches, delta_t, matchtype=''):
        assert not fido_disabled, "Fido module is not available!"
        for (f, s) in matches:
            self.lastFmt = self.fid.get_puid(f)




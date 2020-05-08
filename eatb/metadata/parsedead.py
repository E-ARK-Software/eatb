#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

import lxml

from eatb.utils.datetime import LengthBasedDateFormat
from eatb.utils.fileutils import get_sub_path_from_relative_path


def field_namevalue_pairs_per_file(extract_defs, ead_root_path, ead_file_path):
    eadparser = ParsedEad(ead_root_path, ead_file_path)
    file_elmvalpairs = dict()
    for ed in extract_defs:
        text_access_path = ed['text_access_path'] if 'text_access_path' in ed else None
        is_attribute = ed['is_attribute'] if 'is_attribute' in ed else None
        file_elmvalpairs[ed['solr_field']] = eadparser.dao_path_mdval_tuples(ed['ead_element'], text_access_path, is_attribute)
    result = dict()
    for element_name, file_value_pair_list in file_elmvalpairs.items():
        for file_value_pair in file_value_pair_list:
            if not file_value_pair['path'] in result.keys():
                result[file_value_pair['path']] = []

            reformatted_md_value = file_value_pair['mdvalue']
            if element_name.endswith("_dt"):
                lbdf = LengthBasedDateFormat(file_value_pair['mdvalue'])
                print("DATE: %s" % file_value_pair['mdvalue'])
                reformatted_md_value = lbdf.reformat()
            result[file_value_pair['path']].append({'field_name': element_name, 'field_value': reformatted_md_value})
    return result


class ParsedEad():
    """
    Parsed EAD object
    """
    ead_tree = None
    ead_file_path = None

    def __init__(self, rdir, ead_file_path):
        """

        :param rdir: Path to root directory (relative links in the EAD are evaluated according to this path)
        :param ead_file_path: Path to the EAD metadata file
        """
        self.ns = {'ead': 'http://ead3.archivists.org/schema/',
                   'xlink': 'http://www.w3.org/1999/xlink',
                   'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

        self.root_dir = rdir
        self.ead_tree = None
        self.ead_file_path = ead_file_path
        self._load_ead(ead_file_path)

    def _load_ead(self, ead_file_path):
        """
        Load ead Element tree object

        @type       ead_file_path: ElementTree
        @param      ead_file_path: Parsed EAD
        """
        if not os.path.exists(ead_file_path):
            raise ValueError('The XML file is not available at the given location: %s' % ead_file_path)
        self.ead_tree = lxml.etree.parse(ead_file_path)

    def get_root(self):
        if self.ead_tree is None:
            raise ValueError("Attribute 'ead_tree' of type ElementTree must be initialized")
        return self.ead_tree.getroot()

    def get_dao_elements(self):
        return self.ead_tree.getroot().xpath('//ead:dao', namespaces=self.ns)

    def _first_md_val_ancpath(self, current_elm, md_tag, text_accessor=None, is_attr_text_accessor=False):
        def get_text_val(node):
            if not text_accessor:
                return node.text
            tc_elms = node.findall(text_accessor, namespaces=self.ns)
            return None if len(tc_elms) != 1 else tc_elms[0].text
        parent_elms = current_elm.findall("..")
        if parent_elms is not None and len(parent_elms) == 1:
            parent = parent_elms[0]
            for child in parent:
                if re.match(md_tag, child.xpath('local-name()'), re.IGNORECASE):
                    if is_attr_text_accessor:
                        return child.get(text_accessor)
                    return get_text_val(child)
                for c in child:
                    if re.match(md_tag, c.xpath('local-name()'), re.IGNORECASE):
                        return get_text_val(c)
            if re.match(md_tag, parent.tag, re.IGNORECASE):
                return parent.get(text_accessor)
            return self._first_md_val_ancpath(parent, md_tag, text_accessor,
                                              is_attr_text_accessor)
        return None

    def dao_path_mdval_tuples(self, md_tag, text_val_sub_path=None, is_attr_text_accessor=False):
        dao_elements = self.get_dao_elements()
        result = []
        for dao_elm in dao_elements:
            path = get_sub_path_from_relative_path(self.root_dir, self.ead_file_path, dao_elm.attrib['href'])
            mdval = self._first_md_val_ancpath(dao_elm, md_tag, text_val_sub_path, is_attr_text_accessor)
            if mdval:
                result.append({"path": path, "mdvalue": mdval})
        return result

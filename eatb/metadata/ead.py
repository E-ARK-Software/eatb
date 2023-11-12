#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eatb.metadata.parsed_ead import ParsedEad
from eatb.utils.datetime import LengthBasedDateFormat


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



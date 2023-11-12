import re

from lxml import etree as ET


class ParsedDcat():
    """
    Parsed DCAT
    """
    dcat_tree = None
    dataset_xpath = "/rdf:RDF/dcat:Catalog/dcat:dataset/dcat:Dataset/"
    distribution_xpath = "%sdcat:distribution/dcat:Distribution" % dataset_xpath

    def __init__(self, xml_content):
        """
        Constructor takes root directory as argument; paths in EAD file are relative to this directory.

        @type       xml_content: string
        @param      xml_content: XML file content
        """
        self.ns = {'dcat': 'http://www.w3.org/ns/dcat#', 'foaf': 'http://xmlns.com/foaf/0.1/',
                   'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'owl': 'http://www.w3.org/2002/07/owl#',
                   'locn': 'http://www.w3.org/ns/locn#', 'hydra': 'http://www.w3.org/ns/hydra/core#',
                   'vcard': 'http://www.w3.org/2006/vcard/ns#', 'dmav': 'http://datamarket.at/2017/07/dmav/core#',
                   'dct': 'http://purl.org/dc/terms/'}
        self.dcat_tree = ET.XML(xml_content)

    def get_dataset_property_value(self, property):
        elms = self.dcat_tree.xpath("%s%s" % (self.dataset_xpath, property), namespaces=self.ns)
        if len(elms) == 1:
            return elms[0].text
        raise ValueError("Invalid metadata, data set property '%s' is required." % property)

    def get_dataset_property_values(self, properties):
        return {re.sub(r'[a-z]{1,10}:', '', prop).replace("/", "_"): self.get_dataset_property_value(prop) for prop in properties}

    def get_distribution_property_values(self):
        xpath_expr = "%s" % (self.distribution_xpath)
        elms = self.dcat_tree.xpath(xpath_expr, namespaces=self.ns)
        distr_props = {}
        for elm in elms:
            childs = list(elm.iter())
            dps = {}
            for child in childs:
                tag_name = re.sub(r'{.*}', '', child.tag)
                if tag_name == "license":
                    lic_hash = re.search(r'\/[0-9a-z]*\/$', child.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource']).group(0)[1:-1]
                    dps[tag_name] = lic_hash
                else:
                    dps[tag_name] = child.text.strip() if child.text else ""
            del dps['Distribution']
            distr_props[dps['title']] = dps
        return distr_props

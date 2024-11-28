import os
from xml.dom import minidom
from xml.dom.minidom import parseString
from xml.etree import ElementTree
from lxml import etree
import lxml.etree as ET

from eatb.utils.fileutils import read_file_content


def pretty_xml_string(xml_string):
    xml = parseString(xml_string)
    return xml.toprettyxml()

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def rewrite_pretty_xml(xml_file_path):
    parser = ET.XMLParser(resolve_entities=False, remove_blank_text=True, strip_cdata=False)
    parsed_file = ET.parse(xml_file_path, parser)
    xml_file_root = parsed_file.getroot()
    xml_content = ET.tostring(xml_file_root, encoding='UTF-8', pretty_print=True, xml_declaration=True)
    with open(xml_file_path, 'w') as output_file:
        output_file.write(xml_content)
        output_file.close()


def get_xml_schemalocations(xml_file):
    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    xml_dir, tail = os.path.split(xml_file)
    xml_content = read_file_content(xml_file)
    tree = ET.XML(xml_content)
    schema_locs = []
    #Find instances of xsi:schemaLocation
    schema_locations = set(tree.xpath("//*/@xsi:schemaLocation", namespaces={'xsi': XSI}))
    for schema_location in schema_locations:
        namespaces_locations = schema_location.strip().split()
        # Import all fnamspace/schema location pairs
        for namespace, location in zip(*[iter(namespaces_locations)] * 2):
            loc = os.path.abspath(os.path.join(xml_dir, location))
            if not os.path.exists(loc):
                print("ERROR: XML-Schema file not found: %s" % loc)
                raise XMLSchemaNotFound("XML-Schema file not found: %s" % loc)
            schema_locs.append(loc)
    return schema_locs


def change_dcat_element_values(md_file, substitutions):

    xml_content = read_file_content(md_file)
    tree = ET.XML(xml_content)

    for xpath_expr, value in substitutions.iteritems():
        schema_locations = set(tree.xpath(xpath_expr, namespaces={'dct': 'http://purl.org/dc/terms/', 'dcat': 'http://www.w3.org/ns/dcat#'}))
        for schema_location in schema_locations:
            print(schema_location)
            schema_location.text = value
            sl = schema_location
    xml_content = ET.tostring(tree, encoding='UTF-8', pretty_print=True, xml_declaration=True)
    with open(md_file, 'w') as output_file:
        output_file.write(xml_content)
        output_file.close()


def get_dcat_element_values(md_file, substitutions):

    xml_content = read_file_content(md_file)
    tree = ET.XML(xml_content.encode('utf-8'))

    for xpath_expr, value in substitutions.items():
        schema_locations = set(tree.xpath(xpath_expr, namespaces={'dct': 'http://purl.org/dc/terms/', 'dcat': 'http://www.w3.org/ns/dcat#'}))
        for schema_location in schema_locations:
            print(schema_location)
            schema_location.text = value
            sl = schema_location
    xml_content = ET.tostring(tree, encoding='UTF-8', pretty_print=True, xml_declaration=True)
    return xml_content


class XMLSchemaNotFound(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class XmlDictObject(dict):

    def __init__(self, initdict=None):
        if initdict is None:
            initdict = {}
        dict.__init__(self, initdict)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def __str__(self):
        if self.has_key('_text'):
            return self.__getitem__('_text')
        else:
            return ''

    @staticmethod
    def Wrap(x):

        if isinstance(x, dict):
            return XmlDictObject((k, XmlDictObject.Wrap(v)) for (k, v) in x.items())
        elif isinstance(x, list):
            return [XmlDictObject.Wrap(v) for v in x]
        else:
            return x

    @staticmethod
    def _UnWrap(x):
        if isinstance(x, dict):
            return dict((k, XmlDictObject._UnWrap(v)) for (k, v) in x.items())
        elif isinstance(x, list):
            return [XmlDictObject._UnWrap(v) for v in x]
        else:
            return x

    def UnWrap(self):
        return XmlDictObject._UnWrap(self)


def _ConvertDictToXmlRecurse(parent, dictitem):
    assert type(dictitem) is not type([])

    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.items():
            if str(tag) == '_text':
                parent.text = str(child)
            elif type(child) is type([]):
                # iterate through the array and convert
                for listchild in child:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, listchild)
            else:
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _ConvertDictToXmlRecurse(elem, child)
    else:
        parent.text = str(dictitem)


def ConvertDictToXml(xmldict):
    roottag = xmldict.keys()[0]
    root = ElementTree.Element(roottag)
    _ConvertDictToXmlRecurse(root, xmldict[roottag])
    return root


def _ConvertXmlToDictRecurse(node, dictclass):
    nodedict = dictclass()

    if len(node.items()) > 0:
        nodedict.update(dict(node.items()))

    for child in node:
        newitem = _ConvertXmlToDictRecurse(child, dictclass)
        if nodedict.has_key(child.tag):
            if type(nodedict[child.tag]) is type([]):
                nodedict[child.tag].append(newitem)
            else:
                nodedict[child.tag] = [nodedict[child.tag], newitem]
        else:
            nodedict[child.tag] = newitem

    if node.text is None:
        text = ''
    else:
        text = node.text.strip()

    if len(nodedict) > 0:
        if len(text) > 0:
            nodedict['_text'] = text
    else:
        nodedict = text

    return nodedict


def ConvertXmlToDict(root, dictclass=XmlDictObject):
    if type(root) == type(''):
        root = ElementTree.parse(root).getroot()
    elif not isinstance(root, ElementTree.Element):
        raise TypeError('Expected ElementTree.Element or file path string')

    return dictclass({root.tag: _ConvertXmlToDictRecurse(root, dictclass)})


def MetaIdentification(unknown_xml):
    parsed_unknown = ET.parse(unknown_xml)
    unknown_tag =  parsed_unknown.getroot().tag
    tag = unknown_tag.split('}')
    if len(tag) == 2:
        return tag[1]
    if len(tag) == 1:
        return tag[0]


def parse_csip_vocabulary(file_path:str, terms_only:bool=False): 
    """Parse parse_csip_vocabulary vocabulary"""
    try:
        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Define the namespace (based on your XML file)
        ns = {"ns": "https://DILCIS.eu/XML/Vocabularies/IP"}
        
        # Extract vocabulary name
        vocab_name = root.find("ns:Vocabulary", ns).get("Name")
        
        # Prepare the result dictionary
        result = {"VocabularyName": vocab_name, "Entries": []}
        
        # Iterate over entries
        entries = root.findall(".//ns:Entry", ns)
        for entry in entries:
            term = entry.find("ns:Term", ns)
            definition = entry.find("ns:Definition", ns)
            revision_info = entry.find("ns:RevisionInformation", ns)
            source = entry.find("ns:Source", ns)

            # Create an entry dictionary
            entry_dict = {
                "Term": str(term.text).replace("\u2013", "-") if term is not None else None,
                "Definition": definition.text if definition is not None else None,
                "RevisionInformation": {
                    "RevisionDate": revision_info.get("RevisionDate") if revision_info is not None else None,
                    "Text": revision_info.text if revision_info is not None else None,
                },
                "Source": source.text if source is not None else None,
            }
            
            # Add the entry to the result
            result["Entries"].append(entry_dict)
        if terms_only:
            entries = result.get("Entries", [])
            return [entry.get("Term") for entry in entries if "Term" in entry]
        else:
            return result
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

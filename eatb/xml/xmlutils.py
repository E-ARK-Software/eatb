import os
from xml.dom import minidom
from xml.dom.minidom import parseString
from xml.etree import ElementTree

import lxml.etree as ET

from eatb.utils.fileutils import read_file_content
from eatb.xml.xmlschemanotfound import XMLSchemaNotFound


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


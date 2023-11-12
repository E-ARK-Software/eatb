import io
import json
import logging
import os
import re

from importlib_resources import files

import lxml.etree as ET


from lxml import isoschematron
from lxml import etree

from eatb.settings import validation_profile
import eatb.resources
from eatb.utils.fileutils import read_file_content
from eatb.utils.xmlutils import XMLSchemaNotFound


class CSIPValidation(object):

    def __init__(self, rules_path=None):
        if not rules_path:
            self.rules_path = files(eatb.resources).joinpath('validation_rules.xml')
        else:
            self.rules_path = rules_path
        xml_rules = self._read_rules_from_location(rules_path)
        self.rules_lines = xml_rules.split('\n')
        self.validation_report = []
        self.validation_profile = json.loads(validation_profile)
        self.valid = True

    @staticmethod
    def _get_rule(lines, rule_id):
        rules_ids = [rule_id]
        n_header_lines = 5
        rule = lines[:n_header_lines]  # add schema and namespaces
        rule_found = False
        # select all patterns with matching id
        for line in lines[n_header_lines:]:
            if not rule_found:
                # look for beginning of pattern/rule
                match = re.search('pattern id="CSIP(.+?)"', line)
                if match:
                    current_id = int(match.group(1))
                    if current_id in rules_ids:
                        # select pattern
                        rule.append(line)
                        rule_found = True
                    # else ignore pattern
                # else is not the beginning of a pattern
            elif '</pattern>' in line:
                # pattern/rule is over
                rule.append(line)
                rule_found = False
            else:
                rule.append(line)
        rule.append('</schema>\n')
        res = '\n'.join(rule)
        return res

    def _process_validation(self, xml_file, rule_id):
        # Parse rules
        single_rule = io.StringIO(CSIPValidation._get_rule(self.rules_lines, rule_id))
        parsed_single_rule = etree.parse(single_rule)
        schematron = isoschematron.Schematron(parsed_single_rule, store_report=True)

        # Parse XML to validate
        parsed_xml_file = etree.parse(xml_file)
        validation_response = schematron.validate(parsed_xml_file)
        report = schematron.validation_report
        return validation_response, report

    def validate(self, ip_path):
        for validation_block_name, validation_rules in self.validation_profile.items():
            validation_block = {validation_block_name: []}
            for rule_id in validation_rules:
                validation_result, report = self._process_validation(ip_path + '/METS.xml', rule_id=rule_id)
                validation_block[validation_block_name].append(
                    {"rule": "csip%d" % rule_id, "result": validation_result, "report": report}
                )
                # set global validation to 'invalid' if one of the rules is violated
                if not validation_result:
                    self.valid = False
            self.validation_report.append(validation_block)
        return self.validation_report

    def get_validation_profile(self):
        return self.validation_profile

    def get_rules_file_path(self):
        return self.rules_path

    def get_log_lines(self):
        log_lines = []
        for validation_blocks in self.validation_report:
            for validation_block_name, validation_results in validation_blocks.items():
                for validation_result in validation_results:
                    if validation_result['result']:
                        log_lines.append({"type": "INFO", "message": "%s - %s - validated successfully" % (
                        validation_block_name, validation_result['rule'])})
                    else:
                        nsmap = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
                        xml_report = validation_result['report']
                        res = xml_report.find('svrl:failed-assert', namespaces=nsmap)
                        log_lines.append({"type": "ERROR", "message": "%s - %s - Test: %s" % (
                        validation_block_name, validation_result['rule'], res.attrib['test'])})
                        log_lines.append({"type": "ERROR", "message": "%s - %s - Location: %s" % (
                        validation_block_name, validation_result['rule'], res.attrib['location'])})

        return log_lines

    @staticmethod
    def _read_rules_from_location(location):
        if not location:
            return files(eatb.resources).joinpath('validation_rules.xml').read_text()
        with open(location) as fp:
            return fp.read()


class ValidationResult(object):
    def __init__(self, valid, log, err):
        """
        Constructor
        @type       valid: Boolean
        @param      valid: Path to file
        @type       log: List[String]
        @param      log: Processing log
        @type       err: List[String]
        @param      err: Error log
        """
        self.valid = valid
        self.log = log
        self.err = err
    valid = False
    log = []
    err = []


logger = logging.getLogger(__name__)


class XmlValidation(object):
    """
    XML validation class
    """

    XSI = "http://www.w3.org/2001/XMLSchema-instance"
    XS = '{http://www.w3.org/2001/XMLSchema}'

    SCHEMA_TEMPLATE = """<?xml version = "1.0" encoding = "UTF-8"?>
    <schema xmlns="http://www.w3.org/2001/XMLSchema">
    </schema>"""

    def get_schema_from_instance(self, xml):
        xml_dir, tail = os.path.split(xml)

        xml_content = read_file_content(xml)
        tree = ET.XML(xml_content.encode('utf-8'))
        schema_tree = ET.XML(self.SCHEMA_TEMPLATE.encode('utf-8'))

        #Find instances of xsi:schemaLocation
        schema_locations = set(tree.xpath("//*/@xsi:schemaLocation", namespaces={'xsi': self.XSI}))
        for schema_location in schema_locations:
            namespaces_locations = schema_location.strip().split()
            # Import all fnamspace/schema location pairs
            for namespace, location in zip(*[iter(namespaces_locations)] * 2):
                loc = os.path.abspath(os.path.join(xml_dir, location))
                if not os.path.exists(loc):
                    print("ERROR: XML-Schema file not found: %s" % loc)
                    raise XMLSchemaNotFound("XML-Schema file not found: %s" % loc)
                xs_import = ET.Element(self.XS + "import")
                xs_import.attrib['namespace'] = namespace
                xs_import.attrib['schemaLocation'] = loc
                schema_tree.append(xs_import)
        logger.debug("Created schema for validation of instance '%s' from schemaLocation attribute:" % xml)
        logger.debug(ET.tostring(schema_tree, encoding='UTF-8', pretty_print=True, xml_declaration=True))
        return schema_tree

    def validate_XML_by_path(self, xml_path, schema_path):
        """
        This function validates the XML meta data file (parsed_mfile) describing the SIP against the .xsd (sfile),
        which is either contained in the SIP or referenced in the .xml

        @type       xml_path: string
        @param      xml_path: Path to XML file
        @type       schema_path:  string
        @param      schema_path:  Path to schema file.
        @rtype:     ValidationResult
        @return:    Validation result (valid: true/false, processing log, error log)
        """
        validationResult = ValidationResult(False, [], [])
        if schema_path is None:
            validationResult.log.append("XML validation using schemata defined by the schemaLocation attribute.")
        try:
            parsed_schema = ET.parse(schema_path) if schema_path is not None else self.get_schema_from_instance(xml_path)
            parsed_xml = ET.parse(xml_path)
            validationResult = self.validate_XML(parsed_xml, parsed_schema)
        except XMLSchemaNotFound as instance:
            validationResult.err.append("The XML file contains invalid XML-Schema file references. Please verify 'schemaLocation' attribute.")
            validationResult.err.append(instance.parameter)
        except ET.XMLSchemaParseError as xspe:
            # Something wrong with the schema (getting from URL/parsing)
            validationResult.err.append("XMLSchemaParseError occurred!")
            validationResult.err.append(xspe)
        except ET.XMLSyntaxError as xse:
            # XML not well formed
            validationResult.err.append("XMLSyntaxError occurred!")
            validationResult.err.append(xse)
        except Exception as err:
            validationResult.err.append("XML error occurred!")
            validationResult.err.append(err)
        finally:
            return validationResult

    def validate_XML(self, parsed_xml, parsed_schema):
        """
        This function validates the XML meta data file (parsed_mfile) describing the SIP against the .xsd (sfile),
        which is either contained in the SIP or referenced in the .xml

        @type       parsed_xml: ElementTree
        @param      parsed_xml: ElementTree object
        @type       parsed_schema:  ElementTree
        @param      parsed_schema:  Schema file XSD ElementTree object
        @rtype:     bool
        @return:    Validity of XML
        """
        valid_xml = False
        log = []
        err = []
        try:
            # Validate parsed XML against schema returning a readable message on failure
            schema = ET.XMLSchema(parsed_schema)
            # Validate parsed XML against schema returning boolean value indicating success/failure
            log.append('Schema validity: "%s"' % schema.validate(parsed_xml))
            schema.assertValid(parsed_xml)
            valid_xml = True
        except ET.XMLSchemaParseError as xspe:
            # Something wrong with the schema (getting from URL/parsing)
            err.append("XMLSchemaParseError occurred!")
            err.append(xspe)
        except ET.XMLSyntaxError as xse:
            # XML not well formed
            err.append("XMLSyntaxError occurred!")
            err.append(xse)
        except ET.DocumentInvalid as di:
            # XML failed to validate against schema
            err.append("DocumentInvalid occurred!")
            error = schema.error_log.last_error
            if error:
                # All the error properties (from libxml2) describing what went wrong
                err.append('domain_name: ' + error.domain_name)
                err.append('domain: ' + str(error.domain))
                err.append('filename: ' + error.filename)  # '<string>' cos var is a string of xml
                err.append('level: ' + str(error.level))
                err.append('level_name: ' + error.level_name)  # an integer
                err.append('line: ' + str(error.line))  # a unicode string that identifies the line where the error occurred.
                err.append('message: ' + error.message)  # a unicode string that lists the message.
                err.append('type: ' + str(error.type))  # an integer
                err.append('type_name: ' + error.type_name)
        finally:
            return ValidationResult(valid_xml, log, err)

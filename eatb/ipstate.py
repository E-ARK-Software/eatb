#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as Etree

from eatb.utils.xmlutils import prettify
from eatb.utils.datetime import current_timestamp


class IpState():
    """
    TaskExecutionXml class which represents an XML document to persist task execution parameters and results.
    The class can be initiated by parameters (static method from_parameters), by XML content string (static
    method from_content), or by an XML file path (static method from_path). Furthermore, it provides methods
    to manipulate and/or read element values of the XML document.
    """

    doc_content = None
    ted = None

    doc_path = None

    def __init__(self, doc_content, ted):
        self.doc_content = doc_content
        self.ted = ted

    @classmethod
    def from_content(cls, doc_content):
        """
        Alternative constructor (initialise from content string)

        @type doc_content: str
        @param doc_content: doc_content

        @rtype: TaskExecutionXml
        @return: TaskExecutionXml object
        """
        ted = Etree.fromstring(doc_content)
        return cls(doc_content, ted)

    @classmethod
    def from_path(cls, xml_file_path):
        """
        Alternative constructor (initialise from xml file)

        @type xml_file_path: str
        @param xml_file_path: xml_file_path

        @rtype: TaskExecutionXml
        @return: TaskExecutionXml object
        """
        with open(xml_file_path, 'r') as xml_file:
            doc_content = xml_file.read()
        ted = Etree.fromstring(doc_content)
        xml_file.close()
        return cls(doc_content, ted)

    @classmethod
    def from_parameters(cls, state=-1, locked_val=False, last_task_value='None'):
        """
        Alternative constructor (initialise from parameters)
        :param state: state
        :param locked_val: locked val
        :param last_task_value: last task value
        :return:
        """
        doc_content = prettify(cls.create_task_execution_doc(state, locked_val, last_task_value))
        ted = Etree.fromstring(doc_content)
        return cls(doc_content, ted)

    @classmethod
    def create_task_execution_doc(cls, state_val=-1, locked_val=False, last_task_value='None'):
        """
        Alternative constructor (initialise from parameters)
        :param state_val: state val
        :param locked_val: locked val
        :param last_task_value: last task value
        :return:
        """
        ip_state = Element('ip_state')
        state_elm = SubElement(ip_state, 'state')
        state_elm.text = str(state_val)
        locked_elm = SubElement(ip_state, 'locked')
        locked_elm.text = str(locked_val)
        last_task_elm = SubElement(ip_state, 'last_task')
        last_task_elm.text = last_task_value
        return ip_state

    def get_last_task(self):
        """
        Get last task
        :return: last task value
        """
        last_task_elm = self.ted.find('.//last_task')
        last_task_value = 'None' if last_task_elm is None else last_task_elm.text
        return last_task_value

    def set_last_task(self, last_task_value):
        """
        Set document path
        :param last_task_value: last task value
        :return: last task value
        """
        last_task_elm = self.ted.find('.//last_task')
        if last_task_elm is None:
            last_task_elm = SubElement(self.ted, 'last_task')
        last_task_elm.text = last_task_value

    def get_identifier(self):
        """
        Get identifier

        @rtype: str
        @return: identifier
        """
        identifier_elm = self.ted.find('.//identifier')
        identifier_value = 'None' if identifier_elm is None else identifier_elm.text
        return identifier_value

    def set_identifier(self, identifier_value):
        """
        Set identifier
        :param identifier_value: identifier value
        :return: identifier value
        """
        identifier_elm = self.ted.find('.//identifier')
        if identifier_elm is None:
            identifier_elm = SubElement(self.ted, 'identifier')
        identifier_elm.text = identifier_value

    def get_version(self):
        """
        Get version
        :return: version
        """
        version_elm = self.ted.find('.//version')
        version_value = '00000' if version_elm is None else version_elm.text
        return version_value

    def set_version(self, version_value):
        """
        Set version
        :param version_value: version
        :return: version
        """
        version_elm = self.ted.find('.//version')
        if version_elm is None:
            version_elm = SubElement(self.ted, 'version')
        version_elm.text = version_value

    def get_doc_path(self):
        """
        Get document path
        :return: document path
        """
        return self.doc_path

    def set_doc_path(self, doc_path):
        """
        Set document path
        :param doc_path: document path
        :return: document path
        """
        self.doc_path = doc_path

    def get_state(self):
        """
        Get state value.
        :return: state
        """
        return int(self.ted.find('.//state').text)

    def set_state(self, state_value):
        """
        Set state value
        :param state_value: state value
        :return: state value
        """
        state_elm = self.ted.find('.//state')
        if state_elm is None:
            state_elm = SubElement(self.ted, 'state')
        state_elm.text = str(state_value)

    def get_locked(self):
        """
        Get locked status
        :return: locked status
        """
        return self.ted.find('.//locked').text == "True"

    def set_locked(self, locked_value):
        """
        Set locked status
        :param locked_value:
        :return:
        """
        locked_elm = self.ted.find('.//locked')
        if locked_elm is None:
            locked_elm = SubElement(self.ted, 'locked')
        locked_elm.text = str(locked_value)

    def get_lastchange(self):
        """
        Get last change
        :return: last change
        """
        lastchange_elm = self.ted.find('.//lastchange')
        if lastchange_elm is None:
            return ""
        return self.ted.find('.//lastchange').text

    def set_lastchange(self, lastchange_value):
        """
        Set last change
        :param lastchange_value: last change
        :return: last change
        """
        lastchange_elm = self.ted.find('.//lastchange')
        if lastchange_elm is None:
            lastchange_elm = SubElement(self.ted, 'lastchange')
        lastchange_elm.text = str(lastchange_value)

    def get_updated_doc_content(self):
        """
        Get updated document content (from task execution document)
        :return: updated document content
        """
        return Etree.tostring(self.ted, encoding='UTF-8')

    def write_doc(self, xml_file_path):
        """
        Write document to file
        :param xml_file_path: xml file path
        :return: None
        """
        # update timestamp
        self.set_lastchange(current_timestamp())
        xmlstr = minidom.parseString(Etree.tostring(self.ted)).toprettyxml(indent="\t", newl="\n", encoding="UTF-8")
        with open(xml_file_path, 'w') as output_file:
            output_file.write(xmlstr.decode("utf-8"))
        output_file.close()

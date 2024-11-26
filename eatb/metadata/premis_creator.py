#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from lxml import objectify
from eatb.utils.XmlHelper import sequence_insert
from datetime import datetime
from lxml import etree, objectify
from eatb.utils.XmlHelper import q, XSI_NS
from eatb.utils.datetime import ts_date, DT_ISO_FORMAT_FILENAME

PREMIS_NS = 'http://www.loc.gov/premis/v3'
PREMIS_NSMAP = {None: PREMIS_NS}
P = objectify.ElementMaker(
    annotate=False,
    namespace=PREMIS_NS,
    nsmap=PREMIS_NSMAP)


class PremisCreator:

    premis_successor_sections = ['object', 'event', 'agent', 'right']
    working_dir = None

    def __init__(self, working_dir, f=None):
        self.working_dir = working_dir
        if f is None:
            self.root = P.premis(
                {q(XSI_NS, 'schemaLocation'): PREMIS_NS + ' https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd'},
            )
            self.root.set('version', '3.0')
        else:
            self.root = objectify.parse(f).getroot()

    def add_object(self, identifier_value):
        sequence_insert(
            self.root, P.object(
                {q(XSI_NS, 'type'): 'file'},
                P.objectIdentifier(
                    P.objectIdentifierType('LOCAL'),
                    P.objectIdentifierValue(identifier_value)
                ),
            ),
            self.premis_successor_sections
        )

    def add_event(self, identifier_value, outcome, linking_agent, linking_object=None):
        sequence_insert(
            self.root, P.event(
                P.eventIdentifier(
                    P.eventIdentifierType('URN'),
                    P.eventIdentifierValue(identifier_value.format(ts_date(fmt=DT_ISO_FORMAT_FILENAME)))
                ),
                P.eventType,
                P.eventDateTime(datetime.utcnow().isoformat()),
                P.eventOutcomeInformation(
                    P.eventOutcome(outcome)
                ),
                P.linkingAgentIdentifier(
                    P.linkingAgentIdentifierType('URN'),
                    P.linkingAgentIdentifierValue(linking_agent)
                ),

                P.linkingAgentIdentifier(
                    P.linkingObjectIdentifierType('URN'),
                    P.linkingObjectIdentifierValue(linking_object)
                )
                if linking_object is not None else None
            ),
            self.premis_successor_sections
        )

    def add_relationship(self, identifier_value, outcome, linking_agent, linking_object=None):
        sequence_insert(
            self.root, P.event(
                P.eventIdentifier(
                    P.eventIdentifierType('URN'),
                    P.eventIdentifierValue(identifier_value.format(ts_date(fmt=DT_ISO_FORMAT_FILENAME)))
                ),
                P.eventType,
                P.eventDateTime(datetime.utcnow().isoformat()),
                P.eventOutcomeInformation(
                    P.eventOutcome(outcome)
                ),
                P.linkingAgentIdentifier(
                    P.linkingAgentIdentifierType('URN'),
                    P.linkingAgentIdentifierValue(linking_agent)
                ),

                P.linkingAgentIdentifier(
                    P.linkingObjectIdentifierType('URN'),
                    P.linkingObjectIdentifierValue(linking_object)
                )
                if linking_object is not None else None
            ),
            self.premis_successor_sections
        )

    def add_agent(self, identifier_value, agent_name, agent_type):
        sequence_insert(
            self.root, P.agent(
                P.agentIdentifier(
                    P.agentIdentifierType('URN'),
                    P.agentIdentifierValue(identifier_value)
                ),
                P.agentName(agent_name),
                P.agentType(agent_type)
            ),
            self.premis_successor_sections
        )

    def __str__(self):
        return etree.tostring(self.root, encoding='UTF-8', pretty_print=True, xml_declaration=True)

    def to_string(self):
        return etree.tostring(self.root, encoding='UTF-8', pretty_print=True, xml_declaration=True)

    def create(self, path, type, subtype):
        premis_file_name = f"premis_{type}_{subtype}_{ts_date(fmt=DT_ISO_FORMAT_FILENAME)}.xml"
        path_premis = os.path.join(self.working_dir, path, premis_file_name)
        with open(path_premis, 'w', encoding="utf-8") as output_file:
            output_file.write(self.to_string().decode('UTF-8'))



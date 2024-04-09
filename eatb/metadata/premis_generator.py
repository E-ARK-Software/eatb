import hashlib
import os
import uuid
from mimetypes import MimeTypes
from subprocess import PIPE, Popen

from lxml import etree

from eatb.file_format import FormatIdentification
from eatb.metadata.parsed_premis import P
from eatb.settings import fido_enabled
from eatb.utils.XmlHelper import q, XSI_NS
from eatb.utils.datetime import current_timestamp


class PremisGenerator(object):
    fid = FormatIdentification()
    mime = MimeTypes()
    root_path = ""

    def __init__(self, root_path):
        self.root_path = root_path

    def sha256(self, fname):
        hash = hashlib.sha256()
        with open(fname, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return hash.hexdigest()

    def runCommand(self, program, stdin = PIPE, stdout = PIPE, stderr = PIPE):
        result, res_stdout, res_stderr = None, None, None
        try:
            # quote the executable otherwise we run into troubles
            # when the path contains spaces and additional arguments
            # are presented as well.
            # special: invoking bash as login shell here with
            # an unquoted command does not execute /etc/profile

            print('Launching: ' + ' '.join(program))
            process = Popen( program, stdin = stdin, stdout = stdout, stderr = stderr, shell = False)

            res_stdout, res_stderr = process.communicate()
            result = process.returncode
            print('Finished: ' + ' '.join(program))

        except Exception as ex:
            res_stderr = ''.join(str(ex.args))
            result = 1

        if result != 0:
            print('Command failed:' + ''.join(res_stderr))
            raise Exception('Command failed:' + ''.join(res_stderr))

        return result, res_stdout, res_stderr

    def addObject(self, abs_path):
        '''
        Must be called with the absolute path to a file.

        @param abs_path:    absolute file path
        @return:            Premis object
        '''

        hash = self.sha256(abs_path)
        file_url = "%s" % os.path.relpath(abs_path, self.root_path)
        fmt = None
        if fido_enabled:
            fmt = self.fid.identify_file(abs_path)
        size = os.path.getsize(abs_path)
        premis_id = 'ID' + uuid.uuid4().__str__()

        if not fmt:
            fmt = 'fmt/000'

        # create a Premis object
        object = P.object(
            {q(XSI_NS, 'type'): 'file', "xmlID": premis_id},
            P.objectIdentifier(
                P.objectIdentifierType('filepath'),
                P.objectIdentifierValue(file_url)
            ),
            P.objectCharacteristics(
                P.compositionLevel(0),
                P.fixity(
                    P.messageDigestAlgorithm("SHA-256"),
                    P.messageDigest(hash),
                    P.messageDigestOriginator("hashlib")
                ),
                P.size(size),
                P.format(
                    P.formatRegistry(
                        P.formatRegistryName("PRONOM"),
                        P.formatRegistryKey(fmt),
                        P.formatRegistryRole("identification")
                    )
                ),
            ),
        )
        return object

    def addEvent(self, premispath, info):
        '''
        Add an event to an exisiting Premis file (DefaultTask finalize method).

        @param premispath:
        @param info:
        @return:
        '''
        # print type(premispath)

        outcome = info['outcome']
        agent = info['task_name']
        event_type = info['event_type']
        linked_object = info['linked_object']

        premis_path = os.path.join(self.root_path, premispath)
        premis_parsed = etree.parse(premis_path)
        premis_root = premis_parsed.getroot()

        event_id = 'ID' + uuid.uuid4().__str__()
        event = P.event(
            P.eventIdentifier(
                P.eventIdentifierType('local'),
                P.eventIdentifierValue(event_id)),
            P.eventType(event_type),
            P.eventDateTime(current_timestamp()),
            P.eventOutcomeInformation(
                P.eventOutcome(outcome)
            ),
            P.linkingAgentIdentifier(
                P.linkingAgentIdentifierType('software'),
                P.linkingAgentIdentifierValue('Premis Generator')),
            P.linkingObjectIdentifier(
                P.linkingObjectIdentifierType('repository'),
                P.linkingObjectIdentifierValue(linked_object))
        )
        premis_root.insert(len(premis_root) - 1, event)

        str = etree.tostring(premis_root, encoding='UTF-8', pretty_print=True, xml_declaration=True)
        with open(premis_path, 'w') as output_file:
            output_file.write(str.decode('utf-8'))

        return

    def createMigrationPremis(self, premis_info):
        PREMIS_ATTRIBUTES = {"version" : "2.0"}
        premis = P.premis(PREMIS_ATTRIBUTES)
        premis.attrib['{%s}schemaLocation' % XSI_NS] = "info:lc/xmlns/premis-v2 ../../schemas/premis-v2-2.xsd"

        # creates an object that references the package or representation
        # TODO: identifier!
        premis_id = 'ID' + uuid.uuid4().__str__()
        object = P.object(
            {q(XSI_NS, 'type'): 'representation', "xmlID": premis_id},
            P.objectIdentifier(
                P.objectIdentifierType('repository'),
                P.objectIdentifierValue(premis_id)
            ),
        )
        premis.append(object)

        # list of software agents
        software_agents = []

        # parse the migration.xml, add events and objects
        with open(premis_info['info'], mode='rb') as premis_info_entity:
            migrations = etree.iterparse(premis_info_entity, events=('start',))
            eventlist = []
            for event, element in migrations:
                if element.tag == 'migration':
                    event_id = 'ID' + uuid.uuid4().__str__()
                    if self.root_path.endswith(element.attrib['targetrep']):
                        source_object_abs = os.path.join(element.attrib['sourcedir'], element.attrib['file'])
                        source_object_rel = "%s" % os.path.relpath(source_object_abs, self.root_path)
                        target_object_abs = os.path.join(element.attrib['targetdir'], element.attrib['output'])
                        target_object_rel = "%s" % os.path.relpath(target_object_abs, self.root_path)

                        # add agent to list
                        if element.attrib['agent'] not in software_agents:
                            software_agents.append(element.attrib['agent'])

                        # event
                        event = P.event(
                            P.eventIdentifier(
                                P.eventIdentifierType('local'),
                                P.eventIdentifierValue(event_id)),
                            P.eventType('migration'),
                            P.eventDateTime(element.attrib['starttime']),
                            P.eventOutcomeInformation(
                                P.eventOutcome('success')
                            ),
                            P.linkingAgentIdentifier(
                                P.linkingAgentIdentifierType('software'),
                                P.linkingAgentIdentifierValue(element.attrib['agent'])),
                            P.linkingObjectIdentifier(
                                P.linkingObjectIdentifierType('filepath'),
                                P.linkingObjectIdentifierValue(target_object_rel))
                        )
                        eventlist.append(event)

                        # object
                        object = self.addObject(target_object_abs)
                        # add the relationship to the migration event and the source file
                        relationship = P.relationship(
                            P.relationshipType('derivation'),
                            P.relationshipSubType('has source'),
                            P.relatedObjectIdentification(
                                P.relatedObjectIdentifierType('filepath'),
                                P.relatedObjectIdentifierValue(source_object_rel),
                                P.relatedObjectSequence('0')
                            ),
                            P.relatedEventIdentification(
                                P.relatedEventIdentifierType('local'),
                                P.relatedEventIdentifierValue(event_id),
                                P.relatedEventSequence('1')
                            ),
                        )
                        object.append(relationship)

                        premis.append(object)
                    else:
                        pass
                else:
                    pass

            # append all events to premis root - they must be below the objects (due to validation)
            for event in eventlist:
                premis.append(event)

            # add conduit agent
            identifier_value = 'Premis Generator'
            premis.append(P.agent(
                    P.agentIdentifier(
                        P.agentIdentifierType('LOCAL'),
                        P.agentIdentifierValue(identifier_value)
                    ),
                    P.agentName('Premis Generator'),
                    P.agentType('Software')))

            # add software agents
            for agent in software_agents:
                premis.append(P.agent(
                        P.agentIdentifier(
                            P.agentIdentifierType('LOCAL'),
                            P.agentIdentifierValue(agent)
                        ),
                        P.agentName(agent),
                        P.agentType('Software')))

            # create the Premis file
            str = etree.tostring(premis, encoding='UTF-8', pretty_print=True, xml_declaration=True)
            preservation_dir = os.path.join(self.root_path, 'metadata/preservation')
            if not os.path.exists(preservation_dir):
                os.makedirs(preservation_dir)
            path_premis = os.path.join(self.root_path, 'metadata/preservation/premis.xml')
            with open(path_premis, 'w') as output_file:
                output_file.write(str.decode('utf-8'))

            return

    def createPremis(self, path_premis=None):
        PREMIS_ATTRIBUTES = {"version" : "3.0"}
        premis = P.premis(PREMIS_ATTRIBUTES)
        premis.attrib['{%s}schemaLocation' % XSI_NS] = "http://www.loc.gov/premis/v3 https://www.loc.gov/standards/premis/v3/premis-v3-0.xsd"

        # if there are no /data files, this will ensure that there is at least one object (the IP itself)
        premis_id = 'ID' + uuid.uuid4().__str__()
        object = P.object(
            {q(XSI_NS, 'type'): 'representation', "xmlID": premis_id},
            P.objectIdentifier(
                P.objectIdentifierType('repository'),
                P.objectIdentifierValue(premis_id)
            ),
        )
        premis.append(object)

        # create premis objects for files in this representation (self.root_path/data)
        for directory, subdirectories, filenames in os.walk(os.path.join(self.root_path, 'data')):
            for filename in filenames:
                object = self.addObject(os.path.join(directory, filename))
                premis.append(object)

        # # event
        # identifier_value = 'AIP Creation'
        # linking_agent = 'conduit'
        # linking_object=None
        # premis.append(P.event(
        #         P.eventIdentifier(
        #             P.eventIdentifierType('local'),
        #             P.eventIdentifierValue(identifier_value)
        #         ),
        #         P.eventType,
        #         P.eventDateTime(current_timestamp()),
        #         P.linkingAgentIdentifier(
        #             P.linkingAgentIdentifierType('local'),
        #             P.linkingAgentIdentifierValue(linking_agent)
        #         ),
        #
        #         P.linkingAgentIdentifier(
        #             P.linkingAgentIdentifierType('local'),
        #             P.linkingAgentIdentifierValue(linking_object)
        #         )
        #         if linking_object is not None else None
        #     ))

        # add agent
        identifier_value = 'Premis Generator'
        premis.append(P.agent(
            P.agentIdentifier(
                P.agentIdentifierType('LOCAL'),
                P.agentIdentifierValue(identifier_value)
            ),
            P.agentName('Premis Generator'),
            P.agentType('Software')))

        str = etree.tostring(premis, encoding='UTF-8', pretty_print=True, xml_declaration=True)
        preservation_dir = os.path.join(self.root_path, 'metadata/preservation')
        if not os.path.exists(preservation_dir):
            os.makedirs(preservation_dir)

        if not path_premis:
            path_premis = os.path.join(self.root_path, 'metadata/preservation/premis.xml')

        os.makedirs(os.path.dirname(path_premis), exist_ok=True)

        with open(path_premis, 'w') as output_file:
            output_file.write(str.decode('utf-8'))

        return

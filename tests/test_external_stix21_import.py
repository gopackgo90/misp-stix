#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .test_external_stix21_bundles import TestExternalSTIX21Bundles
from ._test_stix import TestSTIX21
from ._test_stix_import import TestExternalSTIX2Import, TestSTIX21Import
from uuid import uuid5


class TestExternalSTIX21Import(TestExternalSTIX2Import, TestSTIX21, TestSTIX21Import):

    ################################################################################
    #                          MISP GALAXIES IMPORT TESTS                          #
    ################################################################################

    def _check_location_galaxy_features(self, galaxies, stix_object, galaxy_type, cluster_value=None):
        self.assertEqual(len(galaxies), 1)
        galaxy = galaxies[0]
        self.assertEqual(len(galaxy.clusters), 1)
        cluster = galaxy.clusters[0]
        self._assert_multiple_equal(galaxy.type, cluster.type, galaxy_type)
        self.assertEqual(
            galaxy.name, self._galaxy_name_mapping(galaxy_type)['name']
        )
        self.assertEqual(
            galaxy.description,
            self._galaxy_name_mapping(galaxy_type)['description']
        )
        if cluster_value is None:
            self.assertEqual(cluster.value, stix_object.name)
        else:
            self.assertEqual(cluster.value, cluster_value)
        if hasattr(stix_object, 'description'):
            self.assertEqual(cluster.description, stix_object.description)
        return cluster.meta

    def test_stix21_bundle_with_attack_pattern_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_attack_pattern_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_ap, indicator, attribute_ap, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_ap)
        killchain = event_ap.kill_chain_phases[0]
        self.assertEqual(
            meta['kill_chain'],
            [f'{killchain.kill_chain_name}:{killchain.phase_name}']
        )
        self.assertEqual(
            meta['external_id'],
            event_ap.external_references[0].external_id
        )
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        self._check_galaxy_features(attribute.galaxies, attribute_ap)
        killchain = attribute_ap.kill_chain_phases[0]
        self.assertEqual(
            meta['kill_chain'],
            [f'{killchain.kill_chain_name}:{killchain.phase_name}']
        )

    def test_stix21_bundle_with_campaign_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_campaign_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_campaign, indicator, attribute_campaign, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_campaign)
        self.assertEqual(meta, {})
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        self._check_galaxy_features(attribute.galaxies, attribute_campaign),
        self.assertEqual(meta, {})

    def test_stix21_bundle_with_course_of_action_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_course_of_action_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_coa, indicator, attribute_coa, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_coa)
        self.assertEqual(
            meta['refs'],
            [reference.url for reference in event_coa.external_references]
        )
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_coa)
        url, external_id = attribute_coa.external_references
        self.assertEqual(meta['refs'], [url.url])
        self.assertEqual(meta['external_id'], external_id.external_id)

    def test_stix21_bundle_with_intrusion_set_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_intrusion_set_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_is, indicator, attribute_is, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_is)
        self.assertEqual(meta['synonyms'], event_is.aliases)
        self.assertEqual(meta['resource_level'], event_is.resource_level)
        self.assertEqual(meta['primary_motivation'], event_is.primary_motivation)
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_is)
        self.assertEqual(meta['synonyms'], attribute_is.aliases)
        self.assertEqual(meta['resource_level'], attribute_is.resource_level)
        self.assertEqual(meta['primary_motivation'], attribute_is.primary_motivation)

    def test_stix21_bundle_with_location_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_location_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_location, indicator, attribute_location, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        country_meta = self._check_location_galaxy_features(
            event.galaxies, event_location, 'country'
        )
        self.assertEqual(country_meta, {})
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        region_meta = self._check_location_galaxy_features(
            attribute.galaxies, attribute_location, 'region',
            cluster_value='154 - Northern Europe'
        )
        self.assertEqual(region_meta, {})

    def test_stix21_bundle_with_malware_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_malware_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_malware, indicator, attribute_malware, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_malware)
        self.assertEqual(meta['malware_types'], event_malware.malware_types)
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_malware)
        self.assertEqual(meta['malware_types'], attribute_malware.malware_types)

    def test_stix21_bundle_with_threat_actor_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_threat_actor_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_ta, indicator, attribute_ta, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_ta)
        self.assertEqual(meta['synonyms'], event_ta.aliases)
        self.assertEqual(meta['roles'], event_ta.roles)
        self.assertEqual(meta['resource_level'], event_ta.resource_level)
        self.assertEqual(meta['primary_motivation'], event_ta.primary_motivation)
        self.assertEqual(meta['threat_actor_types'], event_ta.threat_actor_types)
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_ta)
        self.assertEqual(meta['synonyms'], attribute_ta.aliases)
        self.assertEqual(meta['roles'], attribute_ta.roles)
        self.assertEqual(meta['resource_level'], attribute_ta.resource_level)
        self.assertEqual(meta['primary_motivation'], attribute_ta.primary_motivation)
        self.assertEqual(meta['threat_actor_types'], attribute_ta.threat_actor_types)

    def test_stix21_bundle_with_tool_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_tool_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_tool, indicator, attribute_tool, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_tool)
        killchain = event_tool.kill_chain_phases[0]
        self.assertEqual(
            meta['kill_chain'],
            [f'{killchain.kill_chain_name}:{killchain.phase_name}']
        )
        self.assertEqual(meta['tool_types'], event_tool.tool_types)
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_tool)
        self.assertEqual(
            meta['refs'], [attribute_tool.external_references[0].url]
        )
        killchain = attribute_tool.kill_chain_phases[0]
        self.assertEqual(
            meta['kill_chain'],
            [f'{killchain.kill_chain_name}:{killchain.phase_name}']
        )
        self.assertEqual(meta['tool_types'], attribute_tool.tool_types)

    def test_stix21_bundle_with_vulnerability_galaxy(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_vulnerability_galaxy()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, event_vuln, indicator, attribute_vuln, _ = bundle.objects
        self._check_misp_event_features_from_grouping(event, grouping)
        meta = self._check_galaxy_features(event.galaxies, event_vuln)
        self.assertEqual(
            meta['external_id'], event_vuln.external_references[0].external_id
        )
        self.assertEqual(len(event.attributes), 1)
        attribute = event.attributes[0]
        self.assertEqual(attribute.uuid, indicator.id.split('--')[1])
        meta = self._check_galaxy_features(attribute.galaxies, attribute_vuln)
        self.assertEqual(
            meta['external_id'],
            attribute_vuln.external_references[0].external_id
        )

    ############################################################################
    #                    OBSERVED DATA OBJECTS IMPORT TESTS                    #
    ############################################################################

    def _check_as_attribute(self, attribute, observed_data, autonomous_system):
        self._check_misp_object_fields(attribute, observed_data, autonomous_system)
        self.assertEqual(attribute.type, 'AS')
        self.assertEqual(attribute.value, f'AS{autonomous_system.number}')

    def _check_as_object(self, misp_object, observed_data, autonomous_system):
        self.assertEqual(misp_object.name, 'asn')
        self._check_misp_object_fields(misp_object, observed_data, autonomous_system)
        self._check_as_fields(misp_object, autonomous_system, autonomous_system.id)

    def _check_directory_object(self, misp_object, observed_data, directory):
        self.assertEqual(misp_object.name, 'directory')
        self._check_misp_object_fields(misp_object, observed_data, directory)
        atime, ctime, mtime = self._check_directory_fields(
            misp_object, directory, directory.id
        )
        self.assertEqual(atime, directory.atime)
        self.assertEqual(ctime, directory.ctime)
        self.assertEqual(mtime, directory.mtime)

    def _check_email_address_attribute(self, observed_data, address, email_address):
        self._check_misp_object_fields(address, observed_data, email_address)
        self.assertEqual(address.type, 'email-dst')
        self.assertEqual(address.value, email_address.value)

    def _check_email_address_attribute_with_display_name(
            self, observed_data, address, display_name, email_address):
        self._check_misp_object_fields(
            address, observed_data, email_address,
            f'{email_address.id} - email-dst - {email_address.value}'
        )
        self.assertEqual(address.type, 'email-dst')
        self.assertEqual(address.value, email_address.value)
        self._check_misp_object_fields(
            display_name, observed_data, email_address,
            f'{email_address.id} - email-dst-display-name - {email_address.display_name}'
        )
        self.assertEqual(display_name.type, 'email-dst-display-name')
        self.assertEqual(display_name.value, email_address.display_name)

    def _check_generic_attribute(
            self, observed_data, observable_object, attribute,
            attribute_type, feature='value'):
        self._check_misp_object_fields(attribute, observed_data, observable_object)
        self.assertEqual(attribute.type, attribute_type)
        self.assertEqual(attribute.value, getattr(observable_object, feature))

    def _check_misp_object_fields(
            self, misp_object, observed_data, observable_object, identifier=None):
        if identifier is None:
            self.assertEqual(misp_object.uuid, observable_object.id.split('--')[1])
        else:
            self.assertEqual(misp_object.uuid, uuid5(self._UUIDv4, identifier))
        self.assertEqual(misp_object.comment, f'Observed Data ID: {observed_data.id}')
        if not (observed_data.modified == observed_data.first_observed == observed_data.last_observed):
            self.assertEqual(misp_object.first_seen, observed_data.first_observed)
            self.assertEqual(misp_object.last_seen, observed_data.last_observed)
        self.assertEqual(misp_object.timestamp, observed_data.modified)

    def test_stix21_bundle_with_as_objects(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_as_objects()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, od3, as1, as2, as3, as4 = bundle.objects
        misp_content = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(misp_content), 4)
        m_object, s_object, m_attribute, s_attribute = misp_content
        self._check_as_object(m_object, od1, as1)
        self._check_as_object(s_object, od2, as3)
        self._check_as_attribute(m_attribute, od1, as2)
        self._check_as_attribute(s_attribute, od3, as4)

    def test_stix21_bundle_with_directory_objects(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_directory_objects()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, directory1, directory2, directory3 = bundle.objects
        misp_objects = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(misp_objects), 3)
        referenced_directory, directory, single_directory = misp_objects
        self._check_directory_object(referenced_directory, od1, directory2)
        self._check_directory_object(directory, od1, directory1)
        self._check_directory_object(single_directory, od2, directory3)
        reference1 = directory.references[0]
        self._assert_multiple_equal(
            reference1.referenced_uuid,
            referenced_directory.uuid,
            directory2.id.split('--')[1]
        )
        self.assertEqual(reference1.relationship_type, 'contains')
        reference2 = referenced_directory.references[0]
        self._assert_multiple_equal(
            reference2.referenced_uuid,
            single_directory.uuid,
            directory3.id.split('--')[1]
        )
        self.assertEqual(reference2.relationship_type, 'contains')

    def test_stix21_bundle_with_domain_attributes(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_domain_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, domain_1, domain_2, domain_3 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 3)
        m_domain1, m_domain2, s_domain = attributes
        self._check_generic_attribute(od1, domain_1, m_domain1, 'domain')
        self._check_generic_attribute(od1, domain_2, m_domain2, 'domain')
        self._check_generic_attribute(od2, domain_3, s_domain, 'domain')

    def test_stix21_bundle_with_email_address_objects(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_email_address_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, od3, ea1, ea2, ea3, ea4 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 6)
        mm_address, mm_display_name, ms_address, sm_address, sm_display_name, ss_address = attributes
        self._check_email_address_attribute_with_display_name(
            od1, mm_address, mm_display_name, ea1
        )
        self._check_email_address_attribute(od1, ms_address, ea2)
        self._check_email_address_attribute_with_display_name(
            od2, sm_address, sm_display_name, ea3
        )
        self._check_email_address_attribute(od3, ss_address, ea4)

    def test_stix21_bundle_with_ip_address_attributes(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_ip_address_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, address_1, address_2, address_3 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 3)
        m_ip1, m_ip2, s_ip = attributes
        self._check_generic_attribute(od1, address_1, m_ip1, 'ip-dst')
        self._check_generic_attribute(od1, address_2, m_ip2, 'ip-dst')
        self._check_generic_attribute(od2, address_3, s_ip, 'ip-dst')

    def test_stix21_bundle_with_mac_address_attributes(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_mac_address_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, address_1, address_2, address_3 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 3)
        m_mac1, m_mac2, s_mac = attributes
        self._check_generic_attribute(od1, address_1, m_mac1, 'mac-address')
        self._check_generic_attribute(od1, address_2, m_mac2, 'mac-address')
        self._check_generic_attribute(od2, address_3, s_mac, 'mac-address')

    def test_stix21_bundle_with_mutex_attributes(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_mutex_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, mutex_1, mutex_2, mutex_3 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 3)
        m_mutex1, m_mutex2, s_mutex = attributes
        self._check_generic_attribute(od1, mutex_1, m_mutex1, 'mutex', 'name')
        self._check_generic_attribute(od1, mutex_2, m_mutex2, 'mutex', 'name')
        self._check_generic_attribute(od2, mutex_3, s_mutex, 'mutex', 'name')

    def test_stix21_bundle_with_url_attributes(self):
        bundle = TestExternalSTIX21Bundles.get_bundle_with_url_attributes()
        self.parser.load_stix_bundle(bundle)
        self.parser.parse_stix_bundle()
        event = self.parser.misp_event
        _, grouping, od1, od2, url_1, url_2, url_3 = bundle.objects
        attributes = self._check_misp_event_features_from_grouping(event, grouping)
        self.assertEqual(len(attributes), 3)
        m_url1, m_url2, s_url = attributes
        self._check_generic_attribute(od1, url_1, m_url1, 'url')
        self._check_generic_attribute(od1, url_2, m_url2, 'url')
        self._check_generic_attribute(od2, url_3, s_url, 'url')

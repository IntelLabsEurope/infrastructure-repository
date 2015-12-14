# Copyright 2015 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
OCCI Registry implementation
"""

__author__ = 'gpetralia'

from occi import registry as occi_registry
from api import epa_glue
from api import opendaylight_glue as odl_glue
from api.occi_epa.extensions import epa_addon
from occi import core_model
from occi.exceptions import HTTPError
from occi.core_model import Resource, Link

KIND_TYPE_MAPPING = {
    'stack': epa_addon.STACK,
    'stack_link': epa_addon.STACK_LINK,
    'vm': epa_addon.VM,
    'vm_link': epa_addon.VM_LINK,
    'hypervisor': epa_addon.HYPERVISOR,
    'hypervisor_link': epa_addon.HYPERVISOR_LINK,
    'volume': epa_addon.VOLUME,
    'volume_link': epa_addon.VOLUME_LINK,
    'snapshot': epa_addon.SNAPSHOT,
    'snapshot_link': epa_addon.SNAPSHOT_LINK,
    'cinder-volume': epa_addon.CINDER_VOLUME_SERVICE,
    'cinder-volume_link': epa_addon.CINDER_VOLUME_SERVICE_LINK,
    'port': epa_addon.PORT,
    'port_link': epa_addon.PORT_LINK,
    'router': epa_addon.ROUTER,
    'router_link': epa_addon.ROUTER_LINK,
    'floatingip': epa_addon.FLOATING_IP,
    'floatingip_link': epa_addon.FLOATING_IP_LINK,
    'controller-service': epa_addon.CONTROLLER_SERVICE,
    'controller-service_link': epa_addon.CONTROLLER_SERVICE_LINK,
    'net': epa_addon.NETWORK,
    'net_link': epa_addon.NETWORK_LINK,
    'machine': epa_addon.MACHINE,
    'machine_link': epa_addon.MACHINE_LINK,
    'cache': epa_addon.CACHE,
    'cache_link': epa_addon.CACHE_LINK,
    'core': epa_addon.CORE,
    'core_link': epa_addon.CORE_LINK,
    'bridge': epa_addon.BRIDGE,
    'bridge_link': epa_addon.BRIDGE_LINK,
    'numanode': epa_addon.NUMA_NODE,
    'numanode_link': epa_addon.NUMA_NODE_LINK,
    'socket': epa_addon.SOCKET,
    'socket_link': epa_addon.SOCKET_LINK,
    'pcidev': epa_addon.PCI_DEV,
    'pcidev_link': epa_addon.PCI_DEV_LINK,
    'pu': epa_addon.PU,
    'pu_link': epa_addon.PU_LINK,
    'osdev': epa_addon.OS_DEV,
    'osdev_link': epa_addon.OS_DEV_LINK,
    'pop': epa_addon.POP,
    'pop_link': epa_addon.POP_LINK,
    'switch': epa_addon.SWITCH,
    'switch_link': epa_addon.SWITCH_LINK,
    'switch-interface': epa_addon.SWITCH_INTERFACE,
    'switch-interface_link': epa_addon.SWITCH_INTERFACE_LINK
}


class EPARegistry(occi_registry.NonePersistentRegistry):

    def get_resource(self, key, extras):
        """
        Get single resource kind and call the
        specific kind backend.

        :param key: UUID of the resource
        :param extras: any extras parameters of the call
        :return Resource: OCCI Resource
        """
        # Initialize PoP ID from extras
        if 'pop_id' in extras:
            pop_id = extras['pop_id']
        else:
            pop_id = None

        pop_url = extras['pop_url']
        result = None
        splitted_url = key[1:].split('/')

        # All resources, except PoPs and PoPs links
        # require a PoP ID
        if splitted_url[0] != 'pop' and not pop_id:
            raise HTTPError(400, "Pop-Id missing")

        # Get Resource
        if len(splitted_url) == 2:
            resource_type = splitted_url[0]
            uuid = splitted_url[1]
            uuids = EPARegistry.get_ids(resource_type, pop_url, pop_id)
            if uuid not in uuids:
                raise HTTPError(404, "Resource not found")

            result = self.get_occi_resource(resource_type, uuid)

            # Identify PoP Link
            if resource_type == 'pop':
                for target_link in epa_glue.get_pop_links_target_uuid(pop_url, uuid):
                    self.get_link(resource_type,
                                  result,
                                  target_link[0],
                                  target_link[1],
                                  target_link[2])

            # Identify switch link
            elif resource_type == 'switch':
                for target_uuid in odl_glue.get_switch_interfaces_by_switch_id(pop_url, pop_id, uuid):
                    link_uuid = uuid + '->' + target_uuid
                    self.get_link(resource_type,
                                  result,
                                  target_uuid,
                                  'switch-interface',
                                  link_uuid)

            # Identify switch interface link
            # A switch interface is connected to the switch
            # and can be connected to an osdev
            elif resource_type == 'switch-interface':
                switch_uuid = odl_glue.get_switch_by_interface(pop_url, pop_id, uuid)
                # Link to the switch
                if switch_uuid:
                    switch_link_uuid = uuid + '->' + switch_uuid
                    self.get_link(resource_type,
                                  result,
                                  switch_uuid,
                                  'switch',
                                  switch_link_uuid)

                osdev_uuid = odl_glue.get_os_dev_by_switch_interface(pop_url, pop_id, uuid)
                # Link to the osdev
                if osdev_uuid:
                    osdev_link_uuid = uuid + '->' + osdev_uuid
                    self.get_link(resource_type,
                                  result,
                                  osdev_uuid,
                                  'osdev',
                                  osdev_link_uuid)
            # Identify osdev link
            # An osdev can be connected to a switch interface
            elif resource_type == 'osdev':
                mac = epa_glue.get_mac_by_osdev_uuid(pop_url, pop_id, uuid)
                if mac:
                    switch_interface = odl_glue.get_switch_interface_by_mac(pop_url, pop_id, mac)
                    if switch_interface:
                        link_uuid = uuid + '->' + switch_interface
                        self.get_link(resource_type,
                                      result,
                                      switch_interface,
                                      'switch-interface',
                                      link_uuid)

            # Indentify link for all other resources
            else:
                for target_link in epa_glue.get_links_target_uuid(extras['pop_url'], pop_id, uuid):
                    link_uuid = uuid + '->' + target_link[0]
                    self.get_link(resource_type,
                                  result,
                                  target_link[0],
                                  target_link[1],
                                  link_uuid)

        # Get Link
        elif len(splitted_url) == 3 and splitted_url[1] == 'link':
            link_uuid = splitted_url[2]

            # Not PoP Link
            # Link UUID = source_uuid + '->' + target_uuid
            if '->' in link_uuid:
                source_type = splitted_url[0]
                source_uuid = splitted_url[2].split('->')[0]
                target_uuid = splitted_url[2].split('->')[1]

                # if source_type is switch
                # target type can be only switch interface
                if source_type == 'switch':
                    link_prop = dict()
                    link_prop['target_type'] = 'switch-interface'

                # if source_type is switch
                # target type can be switch and eventually osdev
                elif source_type == 'switch-interface':
                    link_prop = dict()
                    if target_uuid == odl_glue.get_switch_by_interface(pop_url, pop_id, source_uuid):
                        link_prop['target_type'] = 'switch'
                    elif target_uuid == odl_glue.get_os_dev_by_switch_interface(pop_url, pop_id, source_uuid):
                        link_prop['target_type'] = 'osdev'

                # if source_type is switch
                # and target_uuid is of openflow type
                # target_type is a switch
                elif source_type == 'osdev' and 'openflow' in target_uuid:
                    link_prop = dict()
                    link_prop['target_type'] = 'switch-interface'
                else:
                    link_prop = epa_glue.get_link(extras['pop_url'], pop_id, source_uuid, target_uuid)

                # if link_prop is not set
                # the required link does not exist
                if not link_prop:
                    raise HTTPError(404, "Resource Not Found")
                source_entity = self.get_occi_resource(source_type, source_uuid)
                result = self.get_link(source_type,
                                       source_entity,
                                       target_uuid,
                                       link_prop['target_type'],
                                       link_uuid)

            # PoP Link
            else:
                link_result = epa_glue.get_pop_link_source_target(pop_url, link_uuid)
                if link_result and len(link_result) == 2:
                    source = link_result[0]
                    target = link_result[1]
                    source_entity = self.get_occi_resource(splitted_url[0], source)
                    target_entity = self.get_occi_resource(splitted_url[0], target)
                    result = self.get_occi_link(splitted_url[0] + '_link', link_uuid, source_entity, target_entity)

        # If requested resource does not exist
        # raise Resource not found exception
        if result:
            if isinstance(result, Resource) and result.kind.term != 'pop':
                EPARegistry.add_pop_id_to_resource(result, pop_id)
                EPARegistry.add_pop_id_to_links(result.links, pop_id)
            if isinstance(result, Link) and result.kind.term != 'poplink':
                EPARegistry.add_pop_id_to_resource(result, pop_id)
                EPARegistry.add_pop_id_to_link_source(result, pop_id)
                EPARegistry.add_pop_id_to_link_target(result, pop_id)


            return result
        raise HTTPError(404, 'Resource not found: ' + str(key))

    def get_resources(self, extras):
        """
        Get list of resources
        :param extras: any extras parameter to the call
        :return: list of resources
        """
        results = []
        query = extras['query']
        if extras['kind'] != 'pop':
            if 'pop_id' not in extras:
                raise HTTPError(400, "Pop-Id missing")
            results = self.get_resource_entities(extras['pop_url'], extras['pop_id'], [extras['kind']], query)

        elif extras['kind'] == 'pop':
            results = self.get_pops(extras['pop_url'], query)
        return results

    def get_renderer(self, mime_type):
        """
        Get the render of the requested mime type

        :param mime_type: mime type requested
        :return: Render
        """
        if ';' in mime_type:
            mime_type = mime_type.split(';')[0]
        return super(EPARegistry, self).get_renderer(mime_type)

    def get_link(self, source_type, source_entity, target_uuid, target_type, link_uuid):
        """
        Get Link given the link parameters
        :param source_type: kind of the source of the link
        :param source_entity: Resource representing the source
        :param target_uuid: target uuid
        :param target_type: target kind
        :param link_uuid: link identifier
        :return link:
        """
        target_entity = EPARegistry.get_occi_resource(target_type, target_uuid)
        link = self.get_occi_link(source_type + '_link', link_uuid, source_entity, target_entity)
        return link


    @staticmethod
    def add_pop_id_to_link_source(link, pop_id):
        EPARegistry.add_pop_id_to_resource(link.source, pop_id)

    @staticmethod
    def add_pop_id_to_link_target(link, pop_id):
        EPARegistry.add_pop_id_to_resource(link.target, pop_id)

    @staticmethod
    def get_pops(pop_url, query):
        """
        Get a dict containg PoPs and PoPs links

        :param pop_url: url of the PoP DB
        :param query: query parameters
        :return dict: key: pop UUID, values Resource entity
        """
        results = {}
        for uuid in epa_glue.get_pop_ids(pop_url, query):
            entity = EPARegistry.get_occi_resource('pop', uuid)
            results[uuid] = entity

        links = {}
        for uuid in results:
            for target_link in epa_glue.get_pop_links_target_uuid(pop_url, uuid):
                target_uuid = target_link[0]
                target_type = target_link[1]
                link_uuid = target_link[2]
                source_entity = results[uuid]
                kind = source_entity.kind.term + '_link'
                target_entity = EPARegistry.get_occi_resource(target_type, target_uuid)
                links[link_uuid] = EPARegistry.get_occi_link(kind, link_uuid, source_entity, target_entity)

        results.update(links)
        return results.values()

    @staticmethod
    def get_resource_entities(pop_url, pop_id, openstack_types, query):
        """
        Retrieve a list of entities and their links
        for a given list of types
        :param pop_url: Url of PoP DB
        :param pop_id: PoP ID
        :param openstack_types: list of type
        :param query: optional query parameters
        :return dict: keys resources' uuids, values resources' properties
        """
        results = {}
        for resource_type in openstack_types:
            # For switches call Opendaylight
            if resource_type == 'switch':
                for uuid in odl_glue.get_switches_ids(pop_url, pop_id):
                    entity = EPARegistry.get_occi_resource(resource_type, uuid)
                    results[uuid] = entity

            # For switches' interfaces call Opendaylight
            elif resource_type == 'switch-interface':
                for uuid in odl_glue.get_switch_interfaces(pop_url, pop_id):
                    entity = EPARegistry.get_occi_resource(resource_type, uuid)
                    results[uuid] = entity
            # For all others resources query EPA DB
            else:
                for uuid in epa_glue.get_resource_openstack_ids(pop_url, pop_id, resource_type, query):
                    entity = EPARegistry.get_occi_resource(resource_type, uuid)
                    results[uuid] = entity

        # Retrieve links for the resources that should be returned
        links = {}
        for source_uuid in results:
            if results[source_uuid].kind.term == 'switch':
                for target_uuid in odl_glue.get_switch_interfaces_by_switch_id(pop_url, pop_id, source_uuid):
                    target_type = 'switch-interface'
                    link_uuid = source_uuid + '->' + target_uuid
                    source_entity = results[source_uuid]
                    kind = source_entity.kind.term + '_link'
                    target_entity = EPARegistry.get_occi_resource(target_type, target_uuid)
                    links[link_uuid] = EPARegistry.get_occi_link(kind, link_uuid, source_entity, target_entity)
            elif results[source_uuid].kind.term == 'switch-interface':
                switch_uuid = odl_glue.get_switch_by_interface(pop_url, pop_id, source_uuid)
                if switch_uuid:
                    switch_type = 'switch'
                    source_entity = results[source_uuid]
                    kind = source_entity.kind.term + '_link'
                    switch_entity = EPARegistry.get_occi_resource(switch_type, switch_uuid)
                    switch_link_uuid = uuid + '->' + switch_uuid
                    links[switch_link_uuid] = EPARegistry.get_occi_link(kind, switch_link_uuid,
                                                                        results[source_uuid], switch_entity)

                osdev_uuid = odl_glue.get_os_dev_by_switch_interface(pop_url, pop_id, source_uuid)

                if osdev_uuid:
                    osdev_type = 'osdev'
                    osdev_entity = EPARegistry.get_occi_resource(osdev_type, osdev_uuid)
                    osdev_link_uuid = uuid + '->' + osdev_uuid
                    links[osdev_link_uuid] = EPARegistry.get_occi_link(kind, osdev_link_uuid,
                                                                       results[source_uuid], osdev_entity)
            elif results[source_uuid].kind.term == 'osdev':
                mac = epa_glue.get_mac_by_osdev_uuid(pop_url, pop_id, source_uuid)
                if mac:
                    switch_interface = odl_glue.get_switch_interface_by_mac(pop_url, pop_id, mac)
                    if switch_interface:
                        target_uuid = switch_interface
                        target_type = 'switch-interface'
                        link_uuid = source_uuid + '->' + target_uuid
                        source_entity = results[source_uuid]
                        kind = source_entity.kind.term + '_link'
                        target_entity = EPARegistry.get_occi_resource(target_type, target_uuid)
                        links[link_uuid] = EPARegistry.get_occi_link(kind, link_uuid, source_entity, target_entity)
            else:
                for target_link in epa_glue.get_links_target_uuid(pop_url, pop_id, source_uuid):
                    target_uuid = target_link[0]
                    target_type = target_link[1]
                    link_uuid = source_uuid + '->' + target_uuid
                    source_entity = results[source_uuid]
                    kind = source_entity.kind.term + '_link'
                    target_entity = EPARegistry.get_occi_resource(target_type, target_uuid)
                    links[link_uuid] = EPARegistry.get_occi_link(kind, link_uuid, source_entity, target_entity)

        results.update(links)

        EPARegistry.add_pop_id_to_resources(results, pop_id)

        return results.values()

    @staticmethod
    def add_pop_id_to_resources(results, pop_id):
        for result in results:
            results[result].identifier = '/pop/' + pop_id + results[result].identifier

    @staticmethod
    def add_pop_id_to_links(results, pop_id):
        for result in results:
            result.identifier = '/pop/' + pop_id + result.identifier
            EPARegistry.add_pop_id_to_link_target(result, pop_id)

    @staticmethod
    def add_pop_id_to_resource(result, pop_id):
        result.identifier = '/pop/' + pop_id + result.identifier

    @staticmethod
    def get_occi_resource(kind, uuid):
        """
        Get the occi instance of a resource
        :param kind: kind of the resource
        :param uuid: UUID of the resource
        :return Resource: OCCI resource
        """
        kind = kind.lower()
        iden = KIND_TYPE_MAPPING[kind].location + uuid
        entity = core_model.Resource(iden, KIND_TYPE_MAPPING[kind], [])
        return entity

    @staticmethod
    def get_occi_link(kind, link_uuid, source, target):
        """
        Get the OCCI Link
        :param kind: type of the link
        :param link_uuid: uuid of the link
        :param source: source entity
        :param target: target entity
        :return Link: OCCI Link
        """
        iden = KIND_TYPE_MAPPING[kind].location + link_uuid
        link = core_model.Link(iden, KIND_TYPE_MAPPING[kind], [], source, target)
        source.links.append(link)
        return link

    @staticmethod
    def get_entity_by_uuid(uuid, results):
        """
        Get entity from the registry
        :param uuid: UUID of the resource required
        :param results: list of resources in the registry
        :return entity: OCCI entity
        """
        for entity in results:
            entity_uuid = entity.identifier[1:].split('/')[1]
            if entity_uuid == uuid:
                return entity

    @staticmethod
    def get_ids(kind, pop_url, pop_id):
        """
        Return list of IDs for a given kind
        :param kind: Kind of the resources ids required
        :param pop_url: url of the PoP DB
        :param pop_id: PoP ID
        :return list: list of IDs
        """
        results = list()
        if kind == 'switch':
            for existing_uuid in odl_glue.get_switches_ids(pop_url, pop_id):
                results.append(existing_uuid)
        elif kind == 'switch-interface':
            for existing_uuid in odl_glue.get_switch_interfaces(pop_url, pop_id):
                results.append(existing_uuid)
        elif kind == 'pop':
            for existing_uuid in epa_glue.get_pop_ids(pop_url):
                results.append(existing_uuid)
        else:
            for existing_uuid in epa_glue.get_resource_openstack_ids(pop_url, pop_id, kind, []):
                results.append(existing_uuid)
        return results


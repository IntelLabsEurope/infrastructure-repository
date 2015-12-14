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
Module to manage single OpenStack Resources
"""
__author__ = 'gpetralia'

from multiprocessing import Lock
import json

import common.neo4j_resources as neo_resource


mutex = Lock()


class Hypervisor(object):
    """
    Class to Manage Hypervisor
    """
    def __init__(self, hostname):
        self.hostname = hostname
        self.label = 'hypervisor'

    def get_hypervisor(self, graph_db):
        """
        Retrieve the Hypervisor node from the DB
        :param graph_db: Graph DB instance
        :return Node: Hypervisor node
        """
        node = neo_resource.get_node_by_property(graph_db,
                                                 self.label,
                                                 property_key='hostname',
                                                 property_value=self.hostname)
        return node

    def get_or_add_hypervisor(self, graph_db, resource_id, pop, timestamp, properties=None):
        """
        Retrieve or add the Hypervisor node from the DB
        :param graph_db: Graph DB instance
        :param resource_id: ID of the Hypervisor
        :param pop: PoP ID
        :param timestamp: timestamp in epoch
        :param properties: optional properties of the node
        :return Node: Hypervisor node
        """
        if not properties:
            properties = dict()

        with mutex:
            properties['pop'] = pop
            index = (self.label, 'openstack_uuid', 'hypervisor-' + str(resource_id))
            hyperv_node = neo_resource.add_node(graph_db,
                                                index,
                                                timestamp,
                                                properties)

            if self.hostname:
                host_node = HostNode(self.hostname).get_resource(graph_db, timestamp)
                if host_node:
                    neo_resource.add_edge(graph_db, hyperv_node, host_node, timestamp, 'runs_on')
            return hyperv_node


class HostNode(object):
    """
    Class to manage Machine nodes
    """
    def __init__(self, hostname):
        self.hostname = hostname

    def get_resource(self, graph_db, timestamp):
        """
        Retrieve or add machine node
        :param graph_db: Graph DB instance
        :param timestamp: timestamp in epoch
        :return Node: Machine node
        """
        node_name = self.hostname + '_' + 'Machine' + '_0'
        index = ('physical_resource', 'physical_name', node_name)
        node = neo_resource.add_node(graph_db, index, timestamp)
        return node


class OpenstackResource(object):
    """
    Class to manage all OpenStack nodes
    """
    def __init__(self, uuid):
        self.label = 'virtual_resource'
        self.uuid = uuid

    @property
    def index(self):
        """
        Return a tuple that represents the index of the node
        (label, property key, property_value)
        The property_key is the key where the OpenStack UUID is stored.
        The property_value is the actual value of the OpenStack UUID.
        :return tuple: index of the node
        """
        if self.uuid:
            return self.label, 'openstack_uuid', self.uuid
        else:
            return None

    def get_resource(self, graph_db):
        """
        Retrieve the resource from the DB
        :param graph_db: Graph DB instance
        :return Node: Resource node
        """
        node = neo_resource.get_node(graph_db, self.index)
        return node

    def get_or_add_resource(self, graph_db, timestamp, properties=None):
        """
        Retrieve or add the resource
        :param graph_db: Graph DB instance
        :param timestamp: timestamp in epoch
        :param properties: optional properties of the node
        :return node: Resource node
        """
        node = neo_resource.add_node(graph_db, self.index, timestamp, properties=properties)
        return node

    def remove_resource(self, graph_db):
        """
        Remove the resource from the node
        :param graph_db: Graph DB instance
        """
        with mutex:
            neo_resource.delete_node(graph_db, self.index)

    def update_resource(self, graph_db, timestamp, properties=None):
        """
        Update the resource in the DB
        :param graph_db: Graph DB instance
        :param timestamp: timestamp in epoch
        :param properties: optional properties of the node
        :return node: Resource node
        """
        with mutex:
            node = neo_resource.update_node(graph_db, self.index, timestamp, properties=properties)
            return node

    def get_stack(self, graph_db):
        """
        Get the Heat stack who belongs the resource if any
        :param graph_db: Graph DB instance
        :return string: Stack UUID
        """
        result, stack_node = neo_resource.has_edge(graph_db,
                                                   'has_resource',
                                                   'virtual_resource',
                                                   'resource_type',
                                                   'vnf',
                                                   incoming=True,
                                                   index=self.index)
        if result:
            return stack_node['openstack_uuid']

        return None

    def store(self, graph_db, properties, pop, timestamp,
              in_edges=None, out_edges=None, host_nodes=None,
              controller_services=None, hypervisors=None, update=False):
        """
        Store the resource to the Graph DB
        :param graph_db: Graph DB instance
        :param properties: properties of the node
        :param pop: PoP ID
        :param timestamp: timestamp in epoch
        :param in_edges: inward relations
        :param out_edges: outward relations
        :param host_nodes: Machine node where the resource is running on
        :param controller_services: Controller services that manage the resource
        :param hypervisors: hypervisor where the resource is running on, if any
        :param update: if true, it updates an existing node
        """
        with mutex:
            properties['pop'] = pop

            if update:
                openstack_node = neo_resource.update_node(graph_db, self.index, timestamp, properties=properties)
            else:
                openstack_node = neo_resource.add_node(graph_db, self.index, timestamp, properties=properties)

            if openstack_node:
                if in_edges:
                    for in_edge in in_edges:
                        if in_edges[in_edge]['mandatory']:
                            in_node = OpenstackResource(in_edge).get_or_add_resource(graph_db, timestamp)
                        else:
                            in_node = OpenstackResource(in_edge).get_resource(graph_db)
                        if in_node:
                            neo_resource.add_edge(graph_db, in_node, openstack_node, timestamp,
                                                  in_edges[in_edge]['label'])

                if out_edges:
                    for out_edge in out_edges:
                        if out_edges[out_edge]['mandatory']:
                            out_node = OpenstackResource(out_edge).get_or_add_resource(graph_db, timestamp)
                        else:
                            out_node = OpenstackResource(out_edge).get_resource(graph_db)
                        if out_node:
                            neo_resource.add_edge(graph_db, openstack_node, out_node, timestamp,
                                                  out_edges[out_edge]['label'])

                if host_nodes:
                    for host in host_nodes:
                        host_node = HostNode(host).get_resource(graph_db, timestamp)
                        if host_node:
                            neo_resource.add_edge(graph_db, openstack_node, host_node, timestamp, 'runs_on')

                if hypervisors:
                    for host in hypervisors:
                        hypervisor = Hypervisor(host).get_hypervisor(graph_db)
                        if hypervisor:
                            neo_resource.add_edge(graph_db, openstack_node, hypervisor, timestamp, 'deployed_on')

                if controller_services:
                    for service in controller_services:
                        service_node = ControllerService().get_resource_by_type(graph_db, service)
                        if service_node:
                            neo_resource.add_edge(graph_db, service_node, openstack_node,
                                                  timestamp, 'manages')

                if openstack_node.properties['type'] == 'port':
                    if 'profile' in openstack_node.properties['attributes']:
                        port_attributes = json.loads(openstack_node.properties['attributes'])
                        if 'profile' in port_attributes and 'pci_slot' in port_attributes['profile']:
                            pci_dev = neo_resource.get_nodes_by_attribute(graph_db,
                                                                          openstack_node.properties['hostname'],
                                                                          port_attributes['profile']['pci_slot'])

                        if pci_dev and len(pci_dev) == 1:
                            neo_resource.add_edge(graph_db, openstack_node, pci_dev[0],
                                                  timestamp, 'runs_on')
                return openstack_node

    def remove_neighbours(self, graph_db, neighbour_type=None):
        """
        Remove neighbours of the resource
        :param graph_db: Graph DB instance
        :param neighbour_type: optional neighbour type for filtering mechanism
        """
        with mutex:
            neo_resource.remove_neighbours(graph_db, index=self.index, neighbour_type=neighbour_type)


class ControllerService(OpenstackResource):
    """
    Class to manage controller services nodes
    """
    def __init__(self, uuid=None):
        OpenstackResource.__init__(self, uuid)
        self.label = 'controller_service'

    def get_resource_by_type(self, graph_db, service_type):
        """
        Get Controller service of the given type
        :param graph_db: Graph DB instance
        :param service_type: Service type of the wanted node
        :return node: Controller Service node
        """
        node = neo_resource.get_node_by_property(graph_db, self.label, 'name', service_type)
        return node

    def store(self, graph_db, properties, pop, timestamp):
        """
        Store a new controller service in the Graph DB
        :param graph_db: Graph DB instance
        :param properties: properties of the controller node
        :param pop: PoP ID
        :param timestamp: timestamp in epoch
        """
        with mutex:
            if self.uuid:
                properties['pop'] = pop
                controller_service_node = self.get_or_add_resource(graph_db, timestamp, properties)
                host_node = HostNode(properties['hostname']).get_resource(graph_db, timestamp)
                neo_resource.add_edge(graph_db, controller_service_node, host_node,  timestamp, 'runs_on')
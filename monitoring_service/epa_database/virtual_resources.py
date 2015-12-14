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
Module to manage Virtual resources in the infrastructure

"""

__author__ = 'gpetralia'

from common import neo4j_resources as neo_resource
from common.utils import config_section_map
import time
from openstack.nova_db import NovaDb
from openstack.cinder_db import CinderDb
from openstack.glance_db import GlanceDb
from openstack.heat_db import HeatDb
from openstack.keystone_db import KeystoneDb
from openstack.neutron_db import NeutronDb
from openstack_resource import Hypervisor, HostNode, ControllerService, OpenstackResource


class VirtualResources(object):
    def __init__(self, graph_db, config, timestamp=None):
        """
        Initialize Epa DB with Virtual resources
        """
        if timestamp is not None:
            now = timestamp
        else:
            now = time.time()

        self.graph_db = graph_db

        # Remove all virtual resources
        neo_resource.remove_nodes_by_property(graph_db, 'virtual_resource', property_key='index_type', property_value='virtual_resource')
        neo_resource.remove_nodes_by_property(graph_db, 'virtual_resource', property_key='resource_type', property_value='virtual')
        neo_resource.remove_nodes_by_property(graph_db, 'virtual_resource', property_key='resource_type', property_value='vnf')
        neo_resource.remove_nodes_by_property(graph_db, 'virtual_resource', property_key='resource_type', property_value='service')
        neo_resource.remove_nodes_by_property(graph_db, 'controller_service', property_key='resource_type', property_value='service')
        neo_resource.remove_nodes_by_property(graph_db, 'hypervisor', property_key='resource_type', property_value='service')

        # Collect PoP information from config file
        self.pop = config_section_map('PoP', config)['name']

        # Collect controller information from config file
        self.controller_hostname = config_section_map('Openstack', config)['controller_hostname']
        self.controller_ip = config_section_map('Openstack', config)['controller_ip']

        # Collect Openstack DBs information from configuration file
        os_db_host = config_section_map('OpenstackDB', config)['host']
        os_db_nova_usr = config_section_map('OpenstackDB', config)['nova_db_username']
        os_db_nova_pwd = config_section_map('OpenstackDB', config)['nova_db_password']
        os_db_cinder_usr = config_section_map('OpenstackDB', config)['cinder_db_username']
        os_db_cinder_pwd = config_section_map('OpenstackDB', config)['cinder_db_password']
        os_db_neutron_usr = config_section_map('OpenstackDB', config)['neutron_db_username']
        os_db_neutron_pwd = config_section_map('OpenstackDB', config)['neutron_db_password']
        os_db_glance_usr = config_section_map('OpenstackDB', config)['glance_db_username']
        os_db_glance_pwd = config_section_map('OpenstackDB', config)['glance_db_password']
        os_db_keystone_usr = config_section_map('OpenstackDB', config)['keystone_db_username']
        os_db_keystone_pwd = config_section_map('OpenstackDB', config)['keystone_db_password']
        os_db_heat_usr = config_section_map('OpenstackDB', config)['heat_db_username']
        os_db_heat_pwd = config_section_map('OpenstackDB', config)['heat_db_password']
        os_nova_db = config_section_map('OpenstackDB', config)['nova_db']
        os_cinder_db = config_section_map('OpenstackDB', config)['cinder_db']
        os_neutron_db = config_section_map('OpenstackDB', config)['neutron_db']
        os_glance_db = config_section_map('OpenstackDB', config)['glance_db']
        os_keystone_db = config_section_map('OpenstackDB', config)['keystone_db']
        os_heat_db = config_section_map('OpenstackDB', config)['heat_db']

        # Openstack DB wrappers
        self.nova_db = NovaDb(os_db_host, os_db_nova_usr, os_db_nova_pwd, os_nova_db)
        self.cinder_db = CinderDb(os_db_host, os_db_cinder_usr, os_db_cinder_pwd, os_cinder_db)
        self.glance_db = GlanceDb(os_db_host, os_db_glance_usr, os_db_glance_pwd, os_glance_db)
        self.heat_db = HeatDb(os_db_host, os_db_heat_usr, os_db_heat_pwd, os_heat_db)
        self.keystone_db = KeystoneDb(os_db_host, os_db_keystone_usr, os_db_keystone_pwd, os_keystone_db)
        self.neutron_db = NeutronDb(os_db_host, os_db_neutron_usr, os_db_neutron_pwd, os_neutron_db)

        # Adding Virtual resources

        # Controller Service
        add_controller_service(self.keystone_db, self.graph_db, self.pop, self.controller_hostname,
                               self.controller_ip, now)

        # Neutron Networks
        add_networks(self.neutron_db, self.graph_db, self.pop, now)

        # Neutron Ports
        add_ports(self.neutron_db, self.graph_db, self.pop, now)

        # Neutron Floating IPs
        add_neutron_floating_ips(self.neutron_db, self.graph_db, self.pop, now)

        # Neutron Routers
        add_neutron_routers(self.neutron_db, self.graph_db, self.pop, now)

        # Cinder Volume Services
        add_cinder_volume_services(self.cinder_db, self.graph_db, self.pop, now)

        # Cinder Snapshots
        add_cinder_snapshots(self.cinder_db, self.graph_db, self.pop, now)

        # Cinder Volumes
        add_cinder_volumes(self.cinder_db, self.graph_db, self.pop, now)

        # Hypervisors
        add_nova_hypervisors(self.nova_db, self.graph_db, self.pop, now)

        # Nova Virtual Machines
        add_nova_instances(self.nova_db, self.neutron_db, self.graph_db, self.pop, now)

        # Heat Stacks
        add_heat_stacks(self.heat_db, self.keystone_db, self.graph_db, self.pop, now, self.controller_hostname)


def get_host_node(graph_db, hostname, timestamp):
    """
    Create or ritrieve an host node

    :param graph_db: Graph DB instance
    :param hostname: hostname of the machine node to be added
    :param timestamp: timestamp in epoch
    :return host_node: Host node created
    """
    host_node = HostNode(hostname).store(graph_db, timestamp)
    return host_node


def add_controller_service(keystone_db, graph_db, pop, controller_hostname, controller_ip, timestamp, service_type=None):
    """
    Add controller service
    :param keystone_db: connection to Keystone DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param controller_hostname: hostname of the OpenStack Controller
    :param controller_ip: IP of the OpenStack Controller
    :param timestamp: timestamp in epoch
    :param service_type: optional service type to be added
    """
    services = keystone_db.get_controller_services(controller_ip, controller_hostname, service_type)
    for service in services:
        ControllerService(service).store(graph_db, services[service], pop, timestamp)


def add_networks(neutron_db, graph_db, pop, timestamp, uuid=None, update=False):
    """
    Add Neutron Networks
    :param neutron_db: Connection to Neutron DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of Virtual network to be added
    :param update: if it true, it update the existing node

    """
    networks = neutron_db.get_networks(uuid)
    for network in networks:
        controller_services = ['networks']
        out_nodes = dict()
        OpenstackResource(network).store(graph_db, networks[network], pop, timestamp, out_edges=out_nodes,
                                         controller_services=controller_services, update=update)


def add_neutron_floating_ips(neutron_db, graph_db, pop, timestamp, uuid=None, update=False):
    """
    Add Neutron FloatingIP
    :param neutron_db: Connection to Neutron DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the FloatingIP to be added
    :param update: if it true, it update the existing node
    """
    floatings = neutron_db.get_floating_ips(uuid)

    for floating in floatings:
        out_nodes = {}
        if 'network_id' in floatings[floating]['attributes'].keys() \
                and floatings[floating]['attributes']['network_id'] is not None:
            net_node = {
                'mandatory': True,
                'label': 'on_network'
            }
            out_nodes[floatings[floating]['attributes']['network_id']] = net_node

        #Add Floating ip only if
        if 'fixed_port_id' in floatings[floating]['attributes']:
            floating_node = OpenstackResource(floating).store(graph_db, floatings[floating], pop,
                                                              timestamp, out_edges=out_nodes, update=update)
            add_ports(neutron_db, graph_db, pop, timestamp,
                      uuid=floatings[floating]['attributes']['fixed_port_id'], update=True)


def add_neutron_routers(neutron_db, graph_db, pop, timestamp, uuid=None, update=False):
    """
    Add Neutron Routers
    :param neutron_db: Connection to Neutron DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Router to be added
    :param update: if it true, it update the existing node
    """
    routers = neutron_db.get_routers(uuid=uuid)
    for router in routers:
        in_nodes = {}
        out_nodes = {}
        for port_id in routers[router]['attributes']['ports']:
            if port_id is not None:
                port_node = {
                    'mandatory': True,
                    'label': 'has_port'
                }
                out_nodes[port_id] = port_node
                add_ports(neutron_db, graph_db, pop, timestamp, uuid=port_id)

        OpenstackResource(router).store(graph_db, routers[router], pop,timestamp,
                                        in_edges=in_nodes, out_edges=out_nodes, update=update)


def add_ports(neutron_db, graph_db, pop, timestamp, uuid=None, update=False):
    """
    Add Neutron Ports
    :param neutron_db: Connection to Neutron DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Port to be added
    :param update: if it true, it update the existing node
    """
    ports_node = []
    ports = neutron_db.get_ports(uuid)
    for port in ports.keys():
        in_nodes = {}
        out_nodes = {}

        if 'network_id' in ports[port]['attributes'].keys():
            if ports[port]['attributes']['network_id'] is not None:
                net_id = ports[port]['attributes']['network_id']
                net_node = {
                    'mandatory': True,
                    'label': 'on_network'
                }
                out_nodes[net_id] = net_node

        if 'device_id' in ports[port]['attributes'] and ports[port]['attributes']['device_id'] is not None:
            vm_id = ports[port]['attributes']['device_id']
            if len(vm_id) > 0:
                vm_node = {
                    'mandatory': False,
                    'label': 'has_port'
                }
                in_nodes[vm_id] = vm_node

        if 'floatingips' in ports[port]['attributes'].keys():
            for floatingip in ports[port]['attributes']['floatingips']:
                floatingip_node = {
                    'mandatory': True,
                    'label': 'has_floatingip'
                }
                out_nodes[floatingip] = floatingip_node

        port_node = OpenstackResource(port).store(graph_db, ports[port], pop, timestamp,
                                                  in_edges=in_nodes, out_edges=out_nodes, update=update)
        ports_node.append(port_node)

    if len(ports_node) > 0:
        return ports_node[0]


def add_cinder_volume_services(cinder_db, graph_db, pop, timestamp, uuid=None):
    """
    Add Cinder Volume Services
    :param cinder_db: Connection to Cinder DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Cinder Volume Service to be added
    """
    services = cinder_db.get_cinder_volume_services(uuid)
    for service in services:
        allocation = services[service]['hostname']
        OpenstackResource(service).store(graph_db, services[service], pop,
                                         timestamp, host_nodes=[allocation])


def add_cinder_snapshots(cinder_db, graph_db, pop, timestamp, uuid=None):
    """
    Add Cinder Snapshots
    :param cinder_db: Connection to Cinder DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Snapshot to be added
    """
    snapshots = cinder_db.get_cinder_snapshots(uuid=uuid)
    for snap in snapshots:
        in_nodes = {}

        if snapshots[snap]['attributes']['volume_id'] is not None:
            vol_id = snapshots[snap]['attributes']['volume_id']
            vol_node = {
                'mandatory': True, #False,
                'label': 'has_snapshot'
            }
            in_nodes[vol_id] = vol_node
        OpenstackResource(snap).store(graph_db, snapshots[snap], pop, timestamp, in_edges=in_nodes)


def add_cinder_volumes(cinder_db, graph_db, pop, timestamp, uuid=None, update=False):
    """
    Add Cinder Volumes
    :param cinder_db: Connection to Cinder DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Cinder Volums to be added
    :param update: if it is true, it updates the existing node
    """
    volumes = cinder_db.get_cinder_volumes(uuid)
    for vol in volumes:
        out_nodes = {}
        in_nodes = {}
        if volumes[vol]['attributes']['snapshot_id'] is not None:
            snap_id = volumes[vol]['attributes']['snapshot_id']
            snap_node = {
                'mandatory': True,
                'label': 'has_snapshot'
            }
            out_nodes[snap_id] = snap_node
        if volumes[vol]['attributes']['cinder_volume'] is not None:
            cinder_vol_id = volumes[vol]['attributes']['cinder_volume']
            cinder_node = {
                'mandatory': True,
                'label': 'deployed_on'
            }
            out_nodes[cinder_vol_id] = cinder_node
        if volumes[vol]['attributes']['instance_uuid'] is not None:
            instance_id = volumes[vol]['attributes']['instance_uuid']
            instance_node = {
                'mandatory': True, #False,
                'label': 'has_volume'
            }
            in_nodes[instance_id] = instance_node
        OpenstackResource(vol).store(graph_db, volumes[vol], pop, timestamp,
                                     out_edges=out_nodes, in_edges= in_nodes, update=update)


def add_nova_hypervisors(nova_db, graph_db, pop, timestamp, hostname=None):
    """
    Add Nova Hypervisors
    :param cinder_db: Connection to Nova DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param hostname: optional hostname of the Hypervisor to be added
    """
    hypervisors = nova_db.get_hypervisors(hostname)
    for hyperv in hypervisors:
        Hypervisor(hypervisors[hyperv]['hostname']).get_or_add_hypervisor(graph_db, hyperv,
                                                                          pop, timestamp,
                                                                          properties=hypervisors[hyperv])


def add_nova_instances(nova_db, neutron_db, graph_db, pop, timestamp,
                       uuid=None, update=False):
    """
    Add Nova Instances
    :param nova_db: Connection to Nova DB
    :param neutron_db: Connection to Neutron Db
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param uuid: optional UUID of the Nova Instance to be added
    :param update: if it is true, it updates the existing node
    """
    instances = nova_db.get_instances(uuid=uuid)
    for instance in instances:
        host = instances[instance]['hostname']

        if host:
            hypervisors = [host]
        else:
            hypervisors = []

        out_nodes = {}

        instances[instance]['attributes']['ports'] = neutron_db.get_ports_by_instance_uuid(instance)

        for port in instances[instance]['attributes']['ports']:
            port_id = port
            port_node = {
                'mandatory': False,
                'label': 'has_port'
            }
            out_nodes[port_id] = port_node

        OpenstackResource(instance).store(graph_db, instances[instance],
                                          pop, timestamp, out_edges=out_nodes, hypervisors=hypervisors,
                                          update=update)


def add_heat_stacks(heat_db, keystone_db, graph_db, pop, timestamp, controller_hostname, uuid=None):
    """
    Add Heat Stacks
    :param heat_db: Connection to Heat DB
    :param keystone_db: Connection to Keystone DB
    :param graph_db: Graph DB instance
    :param pop: PoP ID
    :param timestamp: timestamp in epoch
    :param controller_hostname: Hostname of the OpenStack controller
    :param uuid: optional UUID of the Heat Stack to be added
    """
    stacks = heat_db.get_stacks(controller_hostname, keystone_db, uuid)
    for stack in stacks:
        controller_services = ['orchestration']
        out_nodes = {}
        if 'resources' in stacks[stack]['attributes']:
            for resource in stacks[stack]['attributes']['resources']:
                resource_node = {
                    'mandatory': False,
                    'label': 'has_resource'
                }
                out_nodes[resource] = resource_node
        OpenstackResource(stack).store(graph_db, stacks[stack], pop, timestamp,
                                       controller_services=controller_services, out_edges=out_nodes)
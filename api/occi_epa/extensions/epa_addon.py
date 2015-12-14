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
OCCI extension.
It specifies fields for each resource contained in the Epa DB.
"""

__author__ = 'gpetralia'

from occi import core_model

EPA_RESOURCES_ATTRIBUTES = {
    'occi.epa.name':  'immutable',
    'occi.epa.resource_type': 'immutable',
    'occi.epa.category': 'immutable',
    'occi.epa.hostname': 'immutable',
    'occi.epa.attributes': 'immutable',
    'occi.epa.pop_id': 'immutable',
    'occi.epa.pop': 'immutable',
    'occi.epa.timestamp':  'immutable'
}

EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME = {
    'occi.epa.name':  'immutable',
    'occi.epa.resource_type': 'immutable',
    'occi.epa.category': 'immutable',
    'occi.epa.attributes': 'immutable',
    'occi.epa.pop_id': 'immutable',
    'occi.epa.pop': 'immutable',
    'occi.epa.timestamp':  'immutable'
}

STACK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'stack',
    [core_model.Resource.kind],
    [],
    'Stack',
    EPA_RESOURCES_ATTRIBUTES,
    '/stack/'
)

EPA_LINK_ATTRIBUTES = {
    'occi.epa.label': 'immutable'
}

STACK_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'stacklink',
    [core_model.Link.kind],
    [],
    'Link between a stack and its resources',
    EPA_LINK_ATTRIBUTES,
    '/stack/link/'
)

VM = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'vm',
    [core_model.Resource.kind],
    [],
    'Virtual Machine',
    EPA_RESOURCES_ATTRIBUTES,
    '/vm/'
)

VM_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'vmlink',
    [core_model.Link.kind],
    [],
    'Link between a vm and its resources',
    EPA_LINK_ATTRIBUTES,
    '/vm/link/'
)

HYPERVISOR = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'hypervisor',
    [core_model.Resource.kind],
    [],
    'Hypervisor',
    EPA_RESOURCES_ATTRIBUTES,
    '/hypervisor/'
)

HYPERVISOR_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'hypervisorlink',
    [core_model.Link.kind],
    [],
    'Link between an hypervisor and its resources',
    EPA_LINK_ATTRIBUTES,
    '/hypervisor/link/'
)

VOLUME = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'volume',
    [core_model.Resource.kind],
    [],
    'Cinder volume',
    EPA_RESOURCES_ATTRIBUTES,
    '/volume/'
)

VOLUME_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'volumelink',
    [core_model.Link.kind],
    [],
    'Link between a volume and its resources',
    EPA_LINK_ATTRIBUTES,
    '/volume/link/'
)

SNAPSHOT = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'snapshot',
    [core_model.Resource.kind],
    [],
    'Cinder snapshot',
    EPA_RESOURCES_ATTRIBUTES,
    '/snapshot/'
)

SNAPSHOT_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'snapshotlink',
    [core_model.Link.kind],
    [],
    'Link between a snapshot and its resources',
    EPA_LINK_ATTRIBUTES,
    '/snapshot/link/'
)

CINDER_VOLUME_SERVICE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'cinder-volume',
    [core_model.Resource.kind],
    [],
    'Cinder volume service',
    EPA_RESOURCES_ATTRIBUTES,
    '/cinder-volume/'
)

CINDER_VOLUME_SERVICE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'cinder-volumelink',
    [core_model.Link.kind],
    [],
    'Link between a cinder volume service and its resources',
    EPA_LINK_ATTRIBUTES,
    '/cinder-volume/link/'
)

PORT = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'port',
    [core_model.Resource.kind],
    [],
    'Neutron port',
    EPA_RESOURCES_ATTRIBUTES,
    '/port/'
)

PORT_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'portlink',
    [core_model.Link.kind],
    [],
    'Link between a port and its resources',
    EPA_LINK_ATTRIBUTES,
    '/port/link/'
)

ROUTER = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'router',
    [core_model.Resource.kind],
    [],
    'Neutron router',
    EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME,
    '/router/'
)

ROUTER_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'routerlink',
    [core_model.Link.kind],
    [],
    'Link between a router and its resources',
    EPA_LINK_ATTRIBUTES,
    '/router/link/'
)

FLOATING_IP = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'floatingip',
    [core_model.Resource.kind],
    [],
    'Neutron Floating IP',
    EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME,
    '/floatingip/'
)

FLOATING_IP_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'floatingiplink',
    [core_model.Link.kind],
    [],
    'Link between a floating IP and its resources',
    EPA_LINK_ATTRIBUTES,
    '/floatingip/link/'
)

NETWORK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'net',
    [core_model.Resource.kind],
    [],
    'Neutron Network',
    EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME,
    '/net/'
)

NETWORK_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'netlink',
    [core_model.Link.kind],
    [],
    'Link between a network and its resources',
    EPA_LINK_ATTRIBUTES,
    '/network/link/'
)

CONTROLLER_SERVICE_ATTRIBUTES = {
    'occi.epa.name':  'immutable',
    'occi.epa.controller_service': 'immutable',
    'occi.epa.hostname': 'immutable',
    'occi.epa.attributes': 'immutable',
    'occi.epa.pop_id': 'immutable',
    'occi.epa.pop': 'immutable',
    'occi.epa.timestamp': 'immutable',
    'occi.epa.resource_type': 'immutable'
}

CONTROLLER_SERVICE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'controller-service',
    [core_model.Resource.kind],
    [],
    'Openstack Controller service',
    CONTROLLER_SERVICE_ATTRIBUTES,
    '/controller-service/'
)

CONTROLLER_SERVICE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'controller-servicelink',
    [core_model.Link.kind],
    [],
    'Link between a controller service and its resources',
    EPA_LINK_ATTRIBUTES,
    '/controller-service/link/'
)

MACHINE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'machine',
    [core_model.Resource.kind],
    [],
    'Physical machine',
    EPA_RESOURCES_ATTRIBUTES,
    '/machine/'
)

MACHINE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'machinelink',
    [core_model.Link.kind],
    [],
    'Link between a machine and its resources',
    EPA_LINK_ATTRIBUTES,
    '/machine/link/'
)

CACHE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'cache',
    [core_model.Resource.kind],
    [],
    'Physical cache',
    EPA_RESOURCES_ATTRIBUTES,
    '/cache/'
)

CACHE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'cachelink',
    [core_model.Link.kind],
    [],
    'Link between a cache node and its resources',
    EPA_LINK_ATTRIBUTES,
    '/cache/link/'
)

CORE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'core',
    [core_model.Resource.kind],
    [],
    'Physical core',
    EPA_RESOURCES_ATTRIBUTES,
    '/core/'
)

CORE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'corelink',
    [core_model.Link.kind],
    [],
    'Link between a core and its resources',
    EPA_LINK_ATTRIBUTES,
    '/core/link/'
)

BRIDGE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'bridge',
    [core_model.Resource.kind],
    [],
    'PCI Bridge',
    EPA_RESOURCES_ATTRIBUTES,
    '/bridge/'
)

BRIDGE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'bridgelink',
    [core_model.Link.kind],
    [],
    'Link between a PCI bridge and its resources',
    EPA_LINK_ATTRIBUTES,
    '/bridge/link/'
)

NUMA_NODE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'numanode',
    [core_model.Resource.kind],
    [],
    'Numa Node',
    EPA_RESOURCES_ATTRIBUTES,
    '/numanode/'
)

NUMA_NODE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'numanodelink',
    [core_model.Link.kind],
    [],
    'Link between a Numa Node and its resources',
    EPA_LINK_ATTRIBUTES,
    '/numanode/link/'
)

SOCKET = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'socket',
    [core_model.Resource.kind],
    [],
    'Socket',
    EPA_RESOURCES_ATTRIBUTES,
    '/socket/'
)

SOCKET_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'socketlink',
    [core_model.Link.kind],
    [],
    'Link between a socket and its resources',
    EPA_LINK_ATTRIBUTES,
    '/socket/link/'
)

PCI_DEV = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'pcidev',
    [core_model.Resource.kind],
    [],
    'PCI Device',
    EPA_RESOURCES_ATTRIBUTES,
    '/pcidev/'
)

PCI_DEV_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'pcidevlink',
    [core_model.Link.kind],
    [],
    'Link between a PCI device and its resources',
    EPA_LINK_ATTRIBUTES,
    '/pcidev/link/'
)

PU = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'pu',
    [core_model.Resource.kind],
    [],
    'Processing unit',
    EPA_RESOURCES_ATTRIBUTES,
    '/pu/'
)

PU_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'pulink',
    [core_model.Link.kind],
    [],
    'Link between a Processing Unit and its resources',
    EPA_LINK_ATTRIBUTES,
    '/pu/link/'
)

OS_DEV = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'osdev',
    [core_model.Resource.kind],
    [],
    'Operating system device',
    EPA_RESOURCES_ATTRIBUTES,
    '/osdev/'
)

OS_DEV_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'osdevlink',
    [core_model.Link.kind],
    [],
    'Link between a OS device and its resources',
    EPA_LINK_ATTRIBUTES,
    '/osdev/link/'
)

POP_ATTRIBUTES = {
    'occi.epa.pop.name':  '',
    'occi.epa.pop.lat': '',
    'occi.epa.pop.lon': '',
    'occi.epa.pop.graph_db_url': '',
    'occi.epa.timestamp':  'immutable',
    'occi.epa.pop.id':  'immutable',
    'occi.epa.pop.odl_url':  '',
    'occi.epa.pop.odl_name':  '',
    'occi.epa.pop.odl_password':  ''
}

POP = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'pop',
    [core_model.Resource.kind],
    [],
    'Point of Presence',
    POP_ATTRIBUTES,
    '/pop/'
)

POP_LINK_ATTRIBUTES = {
    'occi.epa.timestamp': 'immutable',
    'occi.epa.pop.interface':  '',
    'occi.epa.pop.protocol': '',
    'occi.epa.pop.type': '',
    'occi.epa.pop.source': '',
    'occi.epa.pop.bw_Gps':  '',
    'occi.epa.pop.ip_address':  '',
    'occi.epa.pop.netmask':  '',
    'occi.epa.pop.destination':  '',
    'occi.epa.pop.bw_util_Gps':  '',
    'occi.epa.pop.roundtrip_time_sec':  '',
    'occi.epa.label': 'immutable'
}

POP_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'poplink',
    [core_model.Link.kind],
    [],
    'Link between a POP and another POP',
    POP_LINK_ATTRIBUTES,
    '/pop/link/'
)

SWITCH = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'switch',
    [core_model.Resource.kind],
    [],
    'Physical switch',
    EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME,
    '/switch/'
)

SWITCH_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'switchlink',
    [core_model.Link.kind],
    [],
    'Link between Switch and its interfaces',
    EPA_LINK_ATTRIBUTES,
    '/switch/link/'
)

SWITCH_INTERFACE = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'switch-interface',
    [core_model.Resource.kind],
    [],
    'Physical switch interfaces',
    EPA_RESOURCES_ATTRIBUTES_WO_HOSTNAME,
    '/switch-interface/'
)

SWITCH_INTERFACE_LINK = core_model.Kind(
    'http://schemas.ogf.org/occi/epa#',
    'switch-interfacelink',
    [core_model.Link.kind],
    [],
    'Link between a OS device and its resources',
    EPA_LINK_ATTRIBUTES,
    '/switch-interface/link/'
)
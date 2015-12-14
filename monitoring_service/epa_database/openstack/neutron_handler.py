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
Module to manage Neutron related Events
"""
__author__ = 'gpetralia'

import monitoring_service.epa_database.openstack.openstack_handler as oh
import monitoring_service.epa_database.virtual_resources as virtual_resources
from monitoring_service.epa_database.openstack.neutron_db import NeutronDb
from monitoring_service.epa_database.openstack_resource import OpenstackResource
import time
import json

# List of events related to FloatingIP creation
FLOATINGIP_CREATE_EVENTS = [
    'floatingip.create.end'
]

# List of events related to FloatingIP update
FLOATINGIP_UPDATE_EVENTS = [
    'floatingip.update.end'
]

# List of events related to FloatingIP deletion
FLOATINGIP_DELETE_EVENTS = [
    'floatingip.delete.end'
]

# List of events related to Port creation
PORT_CREATE_EVENTS = [
    'port.create.end'
]

# List of events related to Port update
PORT_UPDATE_EVENTS = [
    'port.update.end'
]

# List of events related to Port deletion
PORT_DELETE_EVENTS = [
    'port.delete.end'
]

# List of events related to Router creation
ROUTER_CREATE_EVENTS = [
    'router.create.end'
]

# List of events related to Router update
ROUTER_UPDATE_EVENTS = [
    'router.update.end'
]

# List of events related to Port deletion
ROUTER_DELETE_EVENTS = [
    'router.delete.end'
]

# List of events related to Router Interfaces
ROUTER_INTERFACE_EVENTS = [
    'router.interface.create',
    'router.interface.delete'
]

# List of events related to Network creation
NETWORK_CREATE_EVENTS = [
    'network.create.end'
]

# List of events related to Network update
NETWORK_UPDATE_EVENTS = [
    'network.update.end'
]

# List of events related to Network deletion
NETWORK_DELETE_EVENTS = [
    'network.delete.end'
]


class FloatingIpHandler(oh.OpenstackHandler):
    """
    Class to manage FloatingIP related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'neutron_db', graph_db)

    @oh.register_handler(FLOATINGIP_UPDATE_EVENTS)
    def handle_floatingip_update(self, graph_db, body):
        """
        Handle the floatingIPs update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['floatingip']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_neutron_floating_ips(neutron_db, graph_db, self.pop, timestamp, uuid=uuid, update=True)

    @oh.register_handler(FLOATINGIP_CREATE_EVENTS)
    def handle_floatingip_create(self, graph_db, body):
        """
        Handle the floatingIPs create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['floatingip']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_neutron_floating_ips(neutron_db, graph_db, self.pop, timestamp, uuid=uuid)

    @oh.register_handler(FLOATINGIP_DELETE_EVENTS)
    def handle_floatingip_delete(self, graph_db, body):
        """
        Handle the floatingIPs delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['floatingip_id']
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_neutron_connection(self):
        """
        create and return the connection to the Neutron DB
        :return NeutronDb:
        """
        neutron_db = NeutronDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return neutron_db


class PortHandler(oh.OpenstackHandler):
    """
    Class to manage Ports related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'neutron_db', graph_db)

    @oh.register_handler(PORT_UPDATE_EVENTS)
    def handle_port_update(self, graph_db, body):
        """
        Handle the ports update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['port']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_ports(neutron_db, graph_db, self.pop, timestamp, uuid=uuid, update=True)

    @oh.register_handler(PORT_CREATE_EVENTS)
    def handle_port_create(self, graph_db, body):
        """
        Handle the ports create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """

        timestamp = time.time()
        uuid = body['payload']['port']['id']
        neutron_db = self.get_neutron_connection()
        port_node = virtual_resources.add_ports(neutron_db, graph_db, self.pop, timestamp, uuid=uuid)
        if port_node and 'network_id' in port_node.properties['attributes']:
            port_node_attributes = json.loads(port_node.properties['attributes'])
            virtual_resources.add_networks(neutron_db,
                                           graph_db,
                                           self.pop,
                                           timestamp,
                                           uuid=port_node_attributes['network_id'],
                                           update=True)

    @oh.register_handler(PORT_DELETE_EVENTS)
    def handle_port_delete(self, graph_db, body):
        """
        Handle the ports delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['port_id']
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_neutron_connection(self):
        """
        create and return the connection to the Neutron DB
        :return NeutronDb:
        """
        neutron_db = NeutronDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return neutron_db


class RouterHandler(oh.OpenstackHandler):
    """
    Class to manage Routers related events
    """

    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'neutron_db', graph_db)

    @oh.register_handler(ROUTER_UPDATE_EVENTS)
    def handle_router_update(self, graph_db, body):
        """
        Handle the routers update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['router']['id']
        neutron_db = self.get_neutron_connection()
        self.update_router(graph_db, neutron_db, uuid, timestamp)

    @oh.register_handler(ROUTER_INTERFACE_EVENTS)
    def handle_interface_update(self, graph_db, body):
        """
        Handle the Routers Interfaces update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['router_interface']['id']
        timestamp = time.time()
        neutron_db = self.get_neutron_connection()
        self.update_router(graph_db, neutron_db, uuid, timestamp)

    @oh.register_handler(ROUTER_CREATE_EVENTS)
    def handle_router_create(self, graph_db, body):
        """
        Handle the routers create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['router']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_neutron_routers(neutron_db, graph_db, self.pop, timestamp, uuid=uuid)

    @oh.register_handler(ROUTER_DELETE_EVENTS)
    def handle_router_delete(self, graph_db, body):
        """
        Handle the routers delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['router_id']
        router = OpenstackResource(uuid)
        router.remove_neighbours(graph_db, neighbour_type='port')
        router.remove_resource(graph_db)

    def update_router(self, graph_db, neutron_db, uuid, timestamp):
        """
        Update Neutron Routers
        :param graph_db: Instance of Graph DB
        :param neutron_db: Instance of NeutronDB
        :param uuid: UUID of the router to be updated
        :param timestamp: timestamp in epoch
        """
        if uuid:
            router = OpenstackResource(uuid)
            router.remove_neighbours(graph_db, neighbour_type='port')
            router.remove_resource(graph_db)
            virtual_resources.add_neutron_routers(neutron_db, graph_db, self.pop, timestamp, uuid=uuid)

    def get_neutron_connection(self):
        """
        create and return the connection to the Neutron DB
        :return NeutronDb:
        """
        neutron_db = NeutronDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return neutron_db


class NetworkHandler(oh.OpenstackHandler):
    """
    Class to manage Networks related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'neutron_db', graph_db)

    @oh.register_handler(NETWORK_UPDATE_EVENTS)
    def handle_network_update(self, graph_db, body):
        """
        Handle the networks update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['network']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_networks(neutron_db, graph_db, self.pop, timestamp, uuid=uuid, update=True)

    @oh.register_handler(NETWORK_CREATE_EVENTS)
    def handle_network_create(self, graph_db, body):
        """
        Handle the networks create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['network']['id']
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_networks(neutron_db, graph_db, self.pop, timestamp, uuid=uuid)

    @oh.register_handler(NETWORK_DELETE_EVENTS)
    def handle_network_delete(self, graph_db, body):
        """
        Handle the networks delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['network_id']
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_neutron_connection(self):
        """
        create and return the connection to the Neutron DB
        :return NeutronDb:
        """
        neutron_db = NeutronDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return neutron_db

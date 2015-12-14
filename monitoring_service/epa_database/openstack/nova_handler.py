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
Module to manage Instances Events
"""

__author__ = 'gpetralia'

import monitoring_service.epa_database.openstack.openstack_handler as oh
import monitoring_service.epa_database.virtual_resources as virtual_resources
from monitoring_service.epa_database.openstack.nova_db import NovaDb
from monitoring_service.epa_database.openstack.neutron_db import NeutronDb
from monitoring_service.epa_database.openstack_resource import OpenstackResource
import time
from common.utils import config_section_map

# List of events related to Instances creation
INSTANCE_CREATE_EVENTS = [
    'compute.instance.create.end'
]

# List of events related to Instances update
INSTANCE_UPDATE_EVENTS = [
    'compute.instance.resize.revert.end',
    'compute.instance.finish_resize.end',
    'compute.instance.rebuild.end',
    'compute.instance.update',
    'compute.instance.exists'
]

# List of events related to Instances deletion
INSTANCE_DELETE_EVENTS = [
    'compute.instance.delete.end'
]


class NovaHandler(oh.OpenstackHandler):
    """
    Class to manage Instances related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'nova_db', graph_db)

    @oh.register_handler(INSTANCE_UPDATE_EVENTS)
    def handle_instance_update(self, graph_db, body):
        """
        Handle the instances update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body["payload"]['instance_id']
        nova_db = self.get_nova_connection()
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_nova_instances(nova_db, neutron_db, graph_db, self.pop, timestamp, uuid=uuid, update=True)
        if 'host' in body["payload"] and body["payload"]['host']:
            virtual_resources.add_nova_hypervisors(nova_db, graph_db, self.pop,
                                                   timestamp, hostname=body["payload"]['host'])

    @oh.register_handler(INSTANCE_CREATE_EVENTS)
    def handle_instance_create(self, graph_db, body):
        """
        Handle the instances create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body["payload"]['instance_id']
        nova_db = self.get_nova_connection()
        neutron_db = self.get_neutron_connection()
        virtual_resources.add_nova_instances(nova_db, neutron_db, graph_db, self.pop, timestamp, uuid=uuid)
        if 'host' in body["payload"] and body["payload"]['host']:
            virtual_resources.add_nova_hypervisors(nova_db, graph_db, self.pop,
                                                   timestamp, hostname=body["payload"]['host'])

    @oh.register_handler(INSTANCE_DELETE_EVENTS)
    def handle_instance_delete(self, graph_db, body):
        """
        Handle the instances delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body["payload"]['instance_id']
        OpenstackResource(uuid).remove_resource(graph_db)
        nova_db = self.get_nova_connection()
        if 'host' in body["payload"] and body["payload"]['host']:
            virtual_resources.add_nova_hypervisors(nova_db, graph_db, self.pop,
                                                   timestamp, hostname=body["payload"]['host'])

    def get_nova_connection(self):
        """
        create and return the connection to the Nova DB
        :return NovaDb:
        """
        nova_db = NovaDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return nova_db

    def get_neutron_connection(self):
        """
        create and return the connection to the Neutron DB
        :return NeutronDb:
        """
        neutron_db_label = config_section_map('OpenstackDB', self.config)['neutron_db']
        neutron_db_usr = config_section_map('OpenstackDB', self.config)['neutron_db_username']
        neutron_db_pwd = config_section_map('OpenstackDB', self.config)['neutron_db_password']
        neutron_db = NeutronDb(self.os_db_host, neutron_db_usr, neutron_db_pwd, neutron_db_label)
        return neutron_db
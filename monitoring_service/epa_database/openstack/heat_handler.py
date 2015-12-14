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

__author__ = 'gpetralia'


import monitoring_service.epa_database.openstack.openstack_handler as oh
import monitoring_service.epa_database.virtual_resources as virtual_resources
from monitoring_service.epa_database.openstack.heat_db import HeatDb
from monitoring_service.epa_database.openstack.keystone_db import KeystoneDb
from monitoring_service.epa_database.openstack_resource import OpenstackResource
import time
from common.utils import config_section_map

# List of events related to Stack creation
ORCHESTRATION_CREATE_EVENTS = [
    'orchestration.stack.create.end'
]

# List of events related to Stack update
ORCHESTRATION_UPDATE_EVENTS = [
    'orchestration.stack.update.end',
    'orchestration.stack.resume.end',
    'orchestration.stack.suspend.end'
]

# List of events related to Stack deletion
ORCHESTRATION_DELETE_EVENTS = [
    'orchestration.stack.delete.end'
]


class OrchestrationHandler(oh.OpenstackHandler):
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'heat_db', graph_db)

    @oh.register_handler(ORCHESTRATION_UPDATE_EVENTS)
    def handle_stack_update(self, graph_db, body):
        """
        Handle the stack update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['stack_identity'].rsplit('/', 1)[1]
        heat_db = self.get_heat_connection()
        keystone_db = self.get_keystone_db(self.config)
        controller_hostname = config_section_map('Openstack', self.config)['controller_hostname']
        OpenstackResource(uuid).remove_resource(graph_db)
        virtual_resources.add_heat_stacks(heat_db, keystone_db, graph_db, self.pop,
                                          timestamp, controller_hostname, uuid=uuid)

    @oh.register_handler(ORCHESTRATION_CREATE_EVENTS)
    def handle_stack_create(self, graph_db, body):
        """
        Handle the stack create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['stack_identity'].rsplit('/', 1)[1]
        heat_db = self.get_heat_connection()
        keystone_db = self.get_keystone_db(self.config)
        controller_hostname = config_section_map('Openstack', self.config)['controller_hostname']
        virtual_resources.add_heat_stacks(heat_db, keystone_db, graph_db, self.pop, timestamp,
                                          controller_hostname, uuid=uuid)

    @oh.register_handler(ORCHESTRATION_DELETE_EVENTS)
    def handle_stack_delete(self, graph_db, body):
        """
        Handle the stack delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['stack_identity'].rsplit('/', 1)[1]
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_heat_connection(self):
        """
        create and return the connection to the Heat DB
        :return HeatDb:
        """
        heat_db = HeatDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return heat_db

    def get_keystone_db(self, config):
        """
        create and return the connection to the Keystone DB
        :param config: Configuration file
        :return KeystoneDb:
        """
        keystone_db_name = config_section_map('OpenstackDB', config)['keystone_db']
        keystone_db_usr = config_section_map('OpenstackDB', config)['keystone_db_username']
        keystone_db_pwd = config_section_map('OpenstackDB', config)['keystone_db_password']
        keystone_db = KeystoneDb(self.os_db_host, keystone_db_usr, keystone_db_pwd, keystone_db_name)
        return keystone_db
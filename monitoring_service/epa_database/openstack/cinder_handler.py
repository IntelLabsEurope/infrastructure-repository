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
Module to manage Cinder Events
"""
__author__ = 'gpetralia'


import monitoring_service.epa_database.openstack.openstack_handler as oh
import monitoring_service.epa_database.virtual_resources as virtual_resources
from monitoring_service.epa_database.openstack.cinder_db import CinderDb
from monitoring_service.epa_database.openstack.keystone_db import KeystoneDb
from monitoring_service.epa_database.openstack.heat_db import HeatDb
from monitoring_service.epa_database.openstack_resource import OpenstackResource
import time
from common.utils import config_section_map

# List of events related to Volume creation
VOLUME_CREATE_EVENTS = [
    'volume.create.end'
]

# List of events related to Volume update
VOLUME_UPDATE_EVENTS = [
    'volume.update.end',
    'volume.resize.end',
    'volume.attach.end',
    'volume.detach.end'
]

# List of events related to Volume delete
VOLUME_DELETE_EVENTS = [
    'volume.delete.end'
]

# List of events related to Snapshot creation
SNAPSHOT_CREATE_EVENTS = [
    'snapshot.create.end'
]

# List of events related to Snapshot update
SNAPSHOT_UPDATE_EVENTS = [
    'snapshot.update.end'
]

# List of events related to Snapshot delete
SNAPSHOT_DELETE_EVENTS = [
    'snapshot.delete.end'
]


class VolumeHandler(oh.OpenstackHandler):
    """
    Class to manage Volume related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'cinder_db', graph_db)

    @oh.register_handler(VOLUME_UPDATE_EVENTS)
    def handle_volume_update(self, graph_db, body):
        """
        Handle the volume update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['volume_id']
        cinder_db = self.get_cinder_connection()
        volume = OpenstackResource(uuid)
        stack_uuid = volume.get_stack(graph_db)
        heat_db = None
        if stack_uuid:
            heat_db = self.get_heat_connection(self.config)
            keystone_db = self.get_keystone_db(self.config)
        OpenstackResource(uuid).remove_resource(graph_db)
        virtual_resources.add_cinder_volumes(cinder_db, graph_db, self.pop, timestamp, uuid=uuid)
        controller_hostname = config_section_map('Openstack', self.config)['controller_hostname']
        if heat_db:
            virtual_resources.add_heat_stacks(heat_db, keystone_db, graph_db, self.pop,
                                              timestamp, controller_hostname, uuid=stack_uuid)

    @oh.register_handler(VOLUME_CREATE_EVENTS)
    def handle_volume_create(self, graph_db, body):
        """
        Handle the volume create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['volume_id']
        cinder_db = self.get_cinder_connection()
        virtual_resources.add_cinder_volumes(cinder_db, graph_db, self.pop, timestamp, uuid=uuid)


    @oh.register_handler(VOLUME_DELETE_EVENTS)
    def handle_volume_delete(self, graph_db, body):
        """
        Handle the volume delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['volume_id']
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_cinder_connection(self):
        """
        create and return the connection to the Cinder DB
        :return CinderDb:
        """
        cinder_db = CinderDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return cinder_db

    def get_heat_connection(self, config):
        """
        create and return the connection to the Heat DB
        :param config: Configuration file
        :return HeatDb:
        """
        heat_db_name = config_section_map('OpenstackDB', config)['heat_db']
        heat_db_usr = config_section_map('OpenstackDB', config)['heat_db_username']
        heat_db_pwd = config_section_map('OpenstackDB', config)['heat_db_password']
        heat_db = HeatDb(self.os_db_host, heat_db_usr, heat_db_pwd, heat_db_name)
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


class SnapshotHandler(oh.OpenstackHandler):
    """
    Class to manage Snapshot related events
    """
    def __init__(self, config, graph_db):
        oh.OpenstackHandler.__init__(self, config, 'cinder_db', graph_db)

    @oh.register_handler(SNAPSHOT_UPDATE_EVENTS)
    def handle_snapshot_update(self, graph_db, body):
        """
        Handle the snapshot update events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['snapshot_id']
        cinder_db = self.get_cinder_connection()
        OpenstackResource(uuid).remove_resource(graph_db)
        virtual_resources.add_cinder_snapshots(cinder_db, graph_db, self.pop, timestamp, uuid=uuid)

    @oh.register_handler(SNAPSHOT_CREATE_EVENTS)
    def handle_snapshot_create(self, graph_db, body):
        """
        Handle the snapshot create events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        timestamp = time.time()
        uuid = body['payload']['snapshot_id']
        cinder_db = self.get_cinder_connection()
        virtual_resources.add_cinder_snapshots(cinder_db, graph_db, self.pop, timestamp, uuid=uuid)


    @oh.register_handler(SNAPSHOT_DELETE_EVENTS)
    def handle_snapshot_delete(self, graph_db, body):
        """
        Handle the snapshot delete events
        :param graph_db: Instance of Graph DB
        :param body: event body
        """
        uuid = body['payload']['snapshot_id']
        OpenstackResource(uuid).remove_resource(graph_db)

    def get_cinder_connection(self):
        """
        create and return the connection to the Cinder DB
        :return CinderDb:
        """
        cinder_db = CinderDb(self.os_db_host, self.os_db_usr, self.os_db_pwd, self.os_db)
        return cinder_db
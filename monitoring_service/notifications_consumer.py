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
Thread Listener of the Openstack notifications
"""

__author__ = 'gpetralia'

from threading import Thread
import pika
import json
from monitoring_service.epa_database.openstack.nova_handler import NovaHandler
from monitoring_service.epa_database.openstack.neutron_handler import FloatingIpHandler
from monitoring_service.epa_database.openstack.neutron_handler import PortHandler
from monitoring_service.epa_database.openstack.neutron_handler import RouterHandler
from monitoring_service.epa_database.openstack.neutron_handler import NetworkHandler
from monitoring_service.epa_database.openstack.cinder_handler import VolumeHandler
from monitoring_service.epa_database.openstack.cinder_handler import SnapshotHandler
from monitoring_service.epa_database.openstack.heat_handler import OrchestrationHandler

handlers_mapping = {
    'compute': NovaHandler,
    'floatingip': FloatingIpHandler,
    'port': PortHandler,
    'router': RouterHandler,
    'network': NetworkHandler,
    'volume': VolumeHandler,
    'snapshot': SnapshotHandler,
    'orchestration': OrchestrationHandler
}


class NotificationsConsumer(Thread):
    """
    Class that creates and runs the notifications consumer
    """
    def __init__(self, rb_username,
                 rb_password,
                 rb_host,
                 rb_port,
                 config,
                 graph_db,
                 notification_queue='notifications.info'):
        """
        NotificationConsumer constructor
        :param rb_username: Openstack RabbitMQ username
        :param rb_password: Openstack RabbitMQ password
        :param rb_host: Openstack RabbitMQ password
        :param rb_port: Openstack RabbitMQ port
        :param config: Epa Controller config file path
        :param graph_db: Instance of Neo4j Epa DB
        :param notification_queue: Openstack RabbitMQ notification queue
        """

        self.delay = 1
        super(NotificationsConsumer, self).__init__()
        self.conn_string = 'amqp://' + \
                           rb_username + ':' \
                           + rb_password + '@' \
                           + rb_host + ':' \
                           + rb_port + '/%2F'

        self.queue = notification_queue
        self.handlers = dict()
        self.before = 0
        self.after = 0

        # Register events' handlers
        for handler in handlers_mapping:
            self.handlers[handler] = handlers_mapping[handler](config, graph_db)

    def consume_notifications(self):
        """
        Start the listener of the notification queue

        """
        queue_name = self.queue
        parameters = pika.URLParameters(self.conn_string)
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        print ' [*] Waiting for OpenStack messages.'
        channel.basic_consume(self.callback,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        """
        Callback called every time a message is received
        and dispatch it to the registered handler

        :param ch: channel
        :param method: method of the message received (Get)
        :param properties: properties of the message received (Get)
        :param body: body of the message received
        """
        body_json = json.loads(body)
        event = body_json['event_type']
        handler = event.split('.')[0]

        if handler in self.handlers:
            self.handlers[handler].handle_events(event, body_json)

    def run(self):
        """
        Start the thread calling the consume notifications

        """
        self.consume_notifications()

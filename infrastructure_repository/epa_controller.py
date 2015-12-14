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

import ConfigParser
import pika
from monitoring_service.agents_consumer import AgentsConsumer
from monitoring_service.notifications_consumer import NotificationsConsumer
from common.utils import config_section_map
from py2neo import neo4j
from monitoring_service.epa_database.virtual_resources import VirtualResources


class EpaController(object):
    """
    EPA controller manages and coordinates its components:
    Neo4j DB, Agents notification listener, OpenStack notification listener.

    """
    def __init__(self, config_file='config/epa_controller.cfg'):

        # Reading configuration
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        rb_usr = config_section_map('RabbitMQ', config)['rb_name']
        rb_pwd = config_section_map('RabbitMQ', config)['rb_password']
        rb_host = config_section_map('RabbitMQ', config)['rb_host']
        rb_port = config_section_map('RabbitMQ', config)['rb_port']
        agents_queue = config_section_map('RabbitMQ', config)['agents_queue']
        self.conn_string = 'amqp://' + \
                           rb_usr + ':' \
                           + rb_pwd + '@' \
                           + rb_host + ':' \
                           + rb_port + '/%2F'

        # Creating agents.info queue

        parameters = pika.URLParameters(self.conn_string)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=agents_queue)

        # Creating connection with neo4j db and init.

        graph_url = config_section_map('EpaDB', config)['epa_url']
        self.graph_db = neo4j.Graph(graph_url)

        self.graph_db.delete_all()

        # Starting AgentsConsumer
        agents_consumer = AgentsConsumer(config, self.graph_db)
        agents_consumer.start()

        # DumpOpenStackDB

        VirtualResources(self.graph_db, config)

        # Starting NotificationsConsumer
        notifications_consumer = NotificationsConsumer(rb_usr, rb_pwd, rb_host, rb_port, config, self.graph_db)
        notifications_consumer.start()
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
Thread Listener of the Agent notifications
"""

__author__ = 'gpetralia'

from threading import Thread
import pika
import json
from common.utils import config_section_map
from epa_database.hw_reources import HostHwResources
import os
import logging

# Name of files created by the agent
DATA_FILES = {
    'dpdk': '_dpdk.txt',
    'hwloc': '_hwloc.xml',
    'cpu': '_cpuinfo.txt',
    'sriov': '_sriov.txt'
}


class AgentsConsumer(Thread):

    def __init__(self, config, graph_db):
        """
        Agent consumer constructor
        :param config: config file instance
        :param graph_db: Graph db instance

        """
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
        super(AgentsConsumer, self).__init__()
        self.config = config
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

        self.queue = agents_queue
        self.graph_db = graph_db

    def consume_agents(self):
        """
        Start the listener of the agents queue

        """
        queue_name = self.queue
        parameters = pika.URLParameters(self.conn_string)
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        print ' [*] Waiting for agents messages.'
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
        if body_json['event_type'] == 'agents.new':
            self.add_new_machine(body_json['hostname'], body_json['data_path'])

    def run(self):
        """
        Start the thread calling consume agents

        """
        self.consume_agents()

    def add_new_machine(self, hostname, data_path):
        """
        Handle the notification received
        starting the adding process of the new machine

        :param hostname: hostname of the machine tobe added
        :param data_path: path where files describing the machine are stored

        """
        pop_name = config_section_map('PoP', self.config)['name']
        hw_resources = HostHwResources(hostname, pop_name, self.graph_db)
        hwloc_file = dpdk_file = sriov_file = cpu_file = None

        for my_file in os.listdir(data_path):
            hostname_file = my_file.split('_')[0]
            file_type = my_file.split('_')[1]
            if hostname_file == hostname:
                if 'hwloc' in file_type:
                    hwloc_file = my_file
                if 'dpdk' in file_type:
                    dpdk_file = my_file
                if 'sriov' in file_type:
                    sriov_file = my_file
                if 'cpuinfo' in file_type:
                    cpu_file = my_file

        hw_resources.store(data_path, hwloc_file, cpu_file, sriov_file, dpdk_file)

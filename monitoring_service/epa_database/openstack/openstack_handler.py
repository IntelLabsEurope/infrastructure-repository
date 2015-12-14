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
Base class for Message handlers
"""

__author__ = 'gpetralia'


from common.utils import config_section_map


handlers = dict()


def register_handler(signal):
    """
    Decorator for registering a function as
    handler for a given signal
    :param signal: take in input a signal or a list of signals
    """
    def wrapper(func):
        if isinstance(signal, list):
            for s in signal:
                handlers[s] = func
        else:
            handlers[signal] = func
            print handlers
        return func
    return wrapper


class OpenstackHandler(object):
    """
    Base Message handler
    """

    def __init__(self, config, db_label, graph_db):
        """
        To init the class pass following params
        :param config: Config file
        :param db_label: name of OS Db where get info
        :param graph_db: Neo4j Graph
        """
        self.config = config
        self.pop = config_section_map('PoP', config)['name']
        self.os_db_host = config_section_map('OpenstackDB', config)['host']
        self.os_db_usr = config_section_map('OpenstackDB', config)[db_label + '_username']
        self.os_db_pwd = config_section_map('OpenstackDB', config)[db_label + '_password']
        self.os_db = config_section_map('OpenstackDB', config)[db_label]
        self.graph_db = graph_db

    def handle_events(self, signal, body):
        """
        Dispatch signal to the register handler.
        :param signal: signal type
        :param body: body of the message
        """
        if signal in handlers:
            print "Handling signal: {}, by_function: {}".format(signal, handlers[signal].__name__)
            handlers[signal](self, self.graph_db, body)

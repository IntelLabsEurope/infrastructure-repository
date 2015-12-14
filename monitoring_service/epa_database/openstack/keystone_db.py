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
Module to get information from Keystone DB
"""
__author__ = 'gpetralia'

import json
from contextlib import closing
import mysql.connector as MySQLdb

class KeystoneDb():
    """
    Exposes methods to get information regarding Keystone resources.
    It manages the connection to the Keystone DB
    """
    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def get_controller_services(self, controller_ip, controller_hostname, service_type=None):
        """
        Return a dict containing the controller services registered to Keystone.
        If an service_type is given, it will return only the service with the given type
        :param controller_ip: IP of the OpenStack Controller
        :param controller_hostname: Hostname of the OpenStack controller
        :param service_type: Optional type of the desired service
        :return dict: contains controller services information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select  service.id, service.extra, service.type, endpoint.interface, endpoint.url ' \
                    'from service join endpoint on service.id = endpoint.service_id ' \
                    'where endpoint.url like "%' + controller_ip + '%" ' \
                    'and ( service.type = "volume" or service.type = "compute" ' \
                    'or service.type = "network" or service.type = "orchestration" or service.type = "image") ' \
                    'and service.enabled = 1'
            if service_type:
                query += ' service.type= "' + service_type + '"'

            cur.execute(query)

            for row in cur.fetchall():
                row_1 = json.loads(row[1])
                if row[0] in res.keys():
                    res[row[0]]['attributes']['endpoints'][row[3]] = row[4]
                else:
                    res[row[0]] = {}
                    res[row[0]]['resource_type'] = 'service'
                    res[row[0]]['type'] = 'controller-service'
                    res[row[0]]['name'] = row[2]
                    res[row[0]]['hostname'] = controller_hostname
                    res[row[0]]['controller_service'] = row[2]
                    res[row[0]]['attributes'] = {}
                    res[row[0]]['attributes']['extra'] = row_1
                    res[row[0]]['attributes']['endpoints'] = {}
                    res[row[0]]['attributes']['endpoints'][row[3]] = row[4]
        return res

    def get_nova_controller_uuid(self):
        """
        Return the  UUID of the Nova controller
        :return string: UUID of Nova controller
        """
        cur = self.conn.cursor()

        query = 'select id from service where type = "compute"'
        cur.execute(query)

        for row in cur.fetchall():
            return row[0]

        return None

    def get_heat_controller_uuid(self):
        """
        Return the  UUID of the Heat controller
        :return string: UUID of Heat controller
        """
        cur = self.conn.cursor()

        query = 'select id from service where type = "orchestration"'
        cur.execute(query)

        for row in cur.fetchall():
            return row[0]

        return None

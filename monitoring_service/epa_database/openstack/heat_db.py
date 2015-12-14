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
Module to get information from Heat DB
"""

__author__ = 'gpetralia'

import json
from contextlib import closing
import mysql.connector as MySQLdb

class HeatDb():
    """
    Exposes methods to get information regarding Heat Stacks.
    It manages the connection to the Heat DB
    """

    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def get_stacks(self, controller_hostname, keystone_db, uuid=None):
        """
        Return a dict containing the stacks stored in Heat.
        If an UUID is given, it will return only the stack with the given UUID
        :param uuid: Optional UUID of the desired stack
        :return dict: contains stacks information
        """
        res = {}
        query = 'select * from stack s join raw_template r on s.raw_template_id = r.id where s.action != "DELETE"'
        with closing(self.conn.cursor()) as cur:
            if uuid:
                query += ' and s.id = "' + uuid + '"'
            cur.execute(query)
            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['attributes'] = {}
                res[row[0]]['hostname'] = controller_hostname
                res[row[0]]['type'] = 'stack'
                res[row[0]]['resource_type'] = 'vnf'
                res[row[0]]['name'] = row[3]
                res[row[0]]['category'] = 'orchestration'
                res[row[0]]['attributes']['status'] = row[8]
                res[row[0]]['attributes']['status_reason'] = row[9]
                res[row[0]]['attributes']['parameters'] = json.loads(row[10])
                res[row[0]]['attributes']['timeout'] = row[11]
                res[row[0]]['attributes']['action'] = row[14]
                res[row[0]]['attributes']['raw_template'] = json.loads(row[21])
                res[row[0]]['attributes']['heat_controller_id'] = keystone_db.get_heat_controller_uuid()

                sub_query = 'select nova_instance from resource where stack_id = "' + row[0] + '"'
                cur.execute(sub_query)
                for sub_row in cur.fetchall():
                    if 'resources' not in res[row[0]]['attributes'].keys():
                        res[row[0]]['attributes']['resources'] = []
                    if sub_row[0]:
                        if ':' in sub_row[0]:
                            resource_id = sub_row[0].split(':')[0]
                        else:
                            resource_id = sub_row[0]
                        res[row[0]]['attributes']['resources'].append(resource_id)

        return res

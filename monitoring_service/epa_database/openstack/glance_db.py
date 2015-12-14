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
Module to get info from Glance DB
"""
__author__ = 'gpetralia'

import json
from contextlib import closing
import mysql.connector as MySQLdb


class GlanceDb():
    """
    Exposes methods to get information regarding Glance Images.
    It manages the connection to the Glance DB.
    """
    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def get_images(self, uuid=None):
        """
        Return a dict containing the images stored in Glance.
        If an UUID is given, it will return only the image with the given UUID
        :param uuid: Optional UUID of the desired image
        :return dict: contains images information
        """
        res = {}

        with closing(self.conn.cursor()) as cur:
            query = 'select * from images join image_locations ' \
                    'on images.id = image_locations.image_id  where images.status != "deleted"'

            if uuid:
                query += ' and images.id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['attributes'] = {}
                res[row[0]]['name'] = row[1]
                res[row[0]]['type'] = 'image'
                res[row[0]]['resource_type'] = 'virtual'
                res[row[0]]['category'] = 'storage'
                res[row[0]]['attributes']['size'] = row[2]
                res[row[0]]['attributes']['status'] = row[3]
                res[row[0]]['attributes']['is_public'] = row[4]
                res[row[0]]['attributes']['disk_format'] = row[9]
                res[row[0]]['attributes']['container_format'] = row[10]
                res[row[0]]['attributes']['checksum'] = row[11]
                res[row[0]]['attributes']['owner'] = row[12]
                res[row[0]]['attributes']['min_disk'] = row[13]
                res[row[0]]['attributes']['min_ram'] = row[14]
                res[row[0]]['attributes']['protected'] = row[15]
                res[row[0]]['attributes']['virtual_size'] = row[16]
                res[row[0]]['attributes']['image_location'] = row[19]
                res[row[0]]['attributes']['meta_data'] = json.loads(row[24])

                sub_query = 'select * from image_properties where image_id="' + row[0] + '"'
                cur.execute(sub_query)

                for sub_row in cur.fetchall():
                    res[row[0]]['attributes'][sub_row[2]] = sub_row[3]

        return res

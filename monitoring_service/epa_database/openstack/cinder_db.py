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
Module to get info from Cinder DB
"""

__author__ = 'gpetralia'

from contextlib import closing
import mysql.connector as MySQLdb


class CinderDb():
    """
    Exposes methods to get information regarding Cinder Resources
    It manages the connection to the Cinder DB.
    """
    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def get_cinder_volume_services(self, uuid=None):
        """
        Get Cinder volume services.
        :param uuid: UUID cinder volume
        """
        res = dict()

        with closing(self.conn.cursor()) as cur:

            query = 'select services.host, services.report_count, services.disabled, ' \
                    'services.availability_zone, services.disabled_reason, services.id from services ' \
                    'where services.binary="cinder-volume"'

            if uuid:
                query += ' and service.id = "' + uuid + '"'

            cur.execute(query)
            for row in cur.fetchall():
                if '@' in row[0]:
                    host = row[0].split('@')[0]
                else:
                    host = row[0]
                index = 'cinder-service-' + str(row[5])
                res[index] = {}
                res[index]['attributes'] = {}
                res[index]['resource_type'] = 'service'
                res[index]['name'] = row[0]
                res[index]['hostname'] = host
                res[index]['category'] = 'storage'
                res[index]['type'] = 'cinder-volume'
                res[index]['attributes'] = {}
                res[index]['attributes']['report_count'] = row[1]
                res[index]['attributes']['disabled'] = row[2]
                res[index]['attributes']['availability_zone'] = row[3]
                res[index]['attributes']['disabled_reason'] = row[4]
        return res

    def get_cinder_snapshots(self, uuid=None):
        """
        Get cinder Snapshots
        :param uuid: uuid of Snapshot
        :return:
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select * from snapshots where deleted != 1'

            if uuid:
                query += ' and id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[4]] = {}
                res[row[4]]['resource_type'] = 'virtual'
                res[row[4]]['name'] = row[12]
                res[row[4]]['category'] = 'storage'
                res[row[4]]['type'] = 'snapshot'
                res[row[4]]['attributes'] = {}
                res[row[4]]['attributes']['volume_id'] = row[5]
                res[row[4]]['attributes']['user_id'] = row[6]
                res[row[4]]['attributes']['project_id'] = row[7]
                res[row[4]]['attributes']['status'] = row[8]
                res[row[4]]['attributes']['progress'] = row[9]
                res[row[4]]['attributes']['volume_size'] = row[10]
                res[row[4]]['attributes']['display_description'] = row[13]
                res[row[4]]['attributes']['provider_location'] = row[14]
                res[row[4]]['attributes']['encryption_key_id'] = row[15]
                res[row[4]]['attributes']['volume_type_id'] = row[16]
                res[row[4]]['attributes']['cgsnapshot_id'] = row[17]
        return res

    def get_cinder_volumes(self, uuid=None):
        """
        Get cinder volume
        :param uuid: UUid of Cinder Volume
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select v.id, v.ec2_id, v.user_id, v.project_id, v.host, v.size, v.availability_zone, ' \
                    'v.instance_uuid, v.mountpoint, v.attach_time, v.status, v.attach_status, v.display_name, ' \
                    'v.display_description, v.provider_location, v.provider_auth, v.snapshot_id, v.volume_type_id, ' \
                    'v.source_volid, v.bootable, v.attached_host, v.provider_geometry, v._name_id, v.encryption_key_id, ' \
                    'v.migration_status, v.replication_status, v.replication_extended_status, v.replication_driver_data, ' \
                    'v.consistencygroup_id from volumes v where v.deleted = 0'

            if uuid:
                query += ' and v.id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['resource_type'] = 'virtual'
                res[row[0]]['name'] = row[12]
                res[row[0]]['type'] = 'volume'
                res[row[0]]['category'] = 'storage'
                res[row[0]]['attributes'] = {}
                res[row[0]]['attributes']['ec2_id'] = row[1]
                res[row[0]]['attributes']['user_id'] = row[2]
                res[row[0]]['attributes']['project_id'] = row[3]

                if '#' in row[4]:
                    cinder_vol = row[4].split('#')[0]
                else:
                    cinder_vol = row[4]

                if '@' in cinder_vol:
                    host = cinder_vol.split('@')[0]
                else:
                    host = cinder_vol

                res[row[0]]['attributes']['cinder_volume'] = cinder_vol
                res[row[0]]['hostname'] = host
                res[row[0]]['attributes']['size'] = row[5]
                res[row[0]]['attributes']['availability_zone'] = row[6]
                res[row[0]]['attributes']['instance_uuid'] = row[7]
                res[row[0]]['attributes']['mountpoint'] = row[8]
                res[row[0]]['attributes']['attach_time'] = row[9]
                res[row[0]]['attributes']['status'] = row[10]
                res[row[0]]['attributes']['attach_status'] = row[11]
                res[row[0]]['attributes']['display_description'] = row[13]
                res[row[0]]['attributes']['provider_location'] = row[14]
                res[row[0]]['attributes']['provider_auth'] = row[15]
                res[row[0]]['attributes']['snapshot_id'] = row[16]
                res[row[0]]['attributes']['volume_type_id'] = row[17]
                res[row[0]]['attributes']['source_volid'] = row[18]
                res[row[0]]['attributes']['bootable'] = row[19]
                res[row[0]]['attributes']['attached_host'] = row[20]
                res[row[0]]['attributes']['provider_geometry'] = row[21]
                res[row[0]]['attributes']['_name_id'] = row[22]
                res[row[0]]['attributes']['encryption_key_id'] = row[23]
                res[row[0]]['attributes']['migration_status'] = row[24]
                res[row[0]]['attributes']['replication_status'] = row[25]
                res[row[0]]['attributes']['replication_extended_status'] = row[26]
                res[row[0]]['attributes']['replication_driver_data'] = row[27]
                res[row[0]]['attributes']['consistencygroup_id'] = row[28]

                sub_query = 'select id from services as s where s.binary = ' \
                    '"cinder-volume" and s.host LIKE "' + cinder_vol + '%"'

                cur.execute(sub_query)
                for sub_row in cur.fetchall():
                    res[row[0]]['attributes']['cinder_volume'] = 'cinder-service-' + str(sub_row[0])
                    break

        return res

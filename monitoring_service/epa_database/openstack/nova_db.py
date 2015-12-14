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
Module to get information from Neutron DB
"""
__author__ = 'gpetralia'

import json
from contextlib import closing
import mysql.connector as MySQLdb

class NovaDb():
    """
    Exposes methods to get information regarding Nova resources.
    It manages the connection to the Nova DB.
    """

    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def __del__(self):
        self.conn.close()

    def instance_is_deleted(self, uuid):
        """
        Return true if the instance is deleted
        :param uuid: UUID of the instance to check
        :return boolean:
        """
        with closing(self.conn.cursor()) as cur:
            query = 'select * from instances i join instance_id_mappings m on i.id = m.id ' \
                    'where m.uuid = "' + uuid + '" and i.deleted = 0'
            cur.execute(query)
            for row in cur.fetchall():
                return False
        return True

    def get_services(self, uuid):

        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'SELECT * FROM services where deleted = 0'

            if uuid:
                query += ' and id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                index = 'nova-service-' + str(row[3])

                res[index] = {}
                res[index]['attributes'] = {}
                res[index]['hostname'] = row[4]
                res[index]['type'] = 'service'
                res[index]['service_type'] = row[5]
                res[index]['resource_type'] = 'service'
                res[index]['name'] = row[5]
                res[index]['attributes']['topic'] = row[6]
                res[index]['attributes']['report_count'] = row[7]
                res[index]['attributes']['disabled'] = row[8]
                res[index]['attributes']['disabled_reason'] = row[10]
        return res

    def get_instances(self, uuid=None):
        """
        Return a dict containing the Instances stored in Nova.
        If an UUID is given, it will return only the Instance with the given UUID
        :param uuid: Optional UUID of the desired Instance
        :return dict: contains Nova Instances information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = "select i.uuid, i.internal_id, i.user_id, i.project_id, i.image_ref, i.kernel_id, i.ramdisk_id, " \
                    "i.launch_index, i.key_name, i.key_data, i.power_state, i.vm_state, i.memory_mb," \
                    "i.vcpus, i.hostname, i.host, i.user_data, i.reservation_id, i.display_name, i.display_description, " \
                    "i.availability_zone, i.locked, i.os_type, i.launched_on, i.instance_type_id, i.vm_mode," \
                    "i.architecture, i.root_device_name, i.access_ip_v4, i.access_ip_v6, i.config_drive," \
                    "i.task_state, i.default_ephemeral_device, i.default_swap_device, i.progress, i.auto_disk_config," \
                    "i.shutdown_terminate, i.disable_terminate, i.root_gb, i.ephemeral_gb, i.cell_name, i.node, i.locked_by," \
                    "i.cleaned, i.ephemeral_key_uuid from instances i where i.deleted = 0"

            if uuid:
                query += ' and i.uuid = "' + uuid + '"'

            cur.execute(query)
            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['attributes'] = {}
                res[row[0]]['type'] = 'vm'
                res[row[0]]['category'] = 'compute'
                res[row[0]]['resource_type'] = 'virtual'
                res[row[0]]['name'] = row[18]  #
                res[row[0]]['hostname'] = row[15]
                res[row[0]]['attributes']['internal_id'] = row[1]
                res[row[0]]['attributes']['user_id'] = row[2]
                res[row[0]]['attributes']['project_id'] = row[3]
                res[row[0]]['attributes']['image_id'] = row[4]  # edge image_id
                res[row[0]]['attributes']['kernel_id'] = row[5]
                res[row[0]]['attributes']['ramdisk_id'] = row[6]
                res[row[0]]['attributes']['launch_index'] = row[7]
                res[row[0]]['attributes']['key_name'] = row[8]
                res[row[0]]['attributes']['key_data'] = row[9]
                res[row[0]]['attributes']['power_state'] = row[10]
                res[row[0]]['attributes']['vm_state'] = row[11]
                res[row[0]]['attributes']['memory_mb'] = row[12]
                res[row[0]]['attributes']['vcpus'] = row[13]
                res[row[0]]['attributes']['hostname'] = row[14]
                res[row[0]]['attributes']['host'] = row[15]
                res[row[0]]['attributes']['reservation_id'] = row[17]
                res[row[0]]['attributes']['display_description'] = row[19]
                res[row[0]]['attributes']['availability_zone'] = row[20]
                res[row[0]]['attributes']['locked'] = row[21]
                res[row[0]]['attributes']['os_type'] = row[22]
                res[row[0]]['attributes']['launched_on'] = row[23]
                res[row[0]]['attributes']['instance_type_id'] = self.get_flavor_uuid(str(row[24]))  # edge instance type
                res[row[0]]['attributes']['vm_mode'] = row[25]
                res[row[0]]['attributes']['architecture'] = row[26]
                res[row[0]]['attributes']['root_device_name'] = row[27]
                res[row[0]]['attributes']['access_ip_v4'] = row[28]
                res[row[0]]['attributes']['access_ip_v6'] = row[29]
                res[row[0]]['attributes']['config_drive'] = row[30]
                res[row[0]]['attributes']['task_state'] = row[31]
                res[row[0]]['attributes']['default_ephemeral_device'] = row[32]
                res[row[0]]['attributes']['default_swap_device'] = row[33]
                res[row[0]]['attributes']['progress'] = row[34]
                res[row[0]]['attributes']['auto_disk_config'] = row[35]
                res[row[0]]['attributes']['shutdown_terminate'] = row[36]
                res[row[0]]['attributes']['disable_terminate'] = row[37]
                res[row[0]]['attributes']['root_gb'] = row[38]
                res[row[0]]['attributes']['ephemeral_gb'] = row[39]
                res[row[0]]['attributes']['cell_name'] = row[40]
                res[row[0]]['attributes']['node'] = row[41]
                res[row[0]]['attributes']['locked_by'] = row[42]
                res[row[0]]['attributes']['cleaned'] = row[43]
                res[row[0]]['attributes']['ephemeral_key_uuid'] = row[44]

            query = 'select * from instance_info_caches'

            if uuid:
                query += ' where instance_uuid = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                if row[5] in res:
                    net_info = json.loads(row[4])
                    for net in net_info:
                        if 'ports' not in res[row[5]]['attributes']:
                            res[row[5]]['attributes']['ports'] = []
                        res[row[5]]['attributes']['ports'].append(net['id'])  # edges ports

        return res

    def get_flavor_uuid(self, flavor_id):
        """
        Return the flavour UUID for a given flavor ID.
        :param flavor_id:
        :return string: Flavor UUID
        """
        with closing(self.conn.cursor()) as cur:
            query = 'select flavorid from instance_types where id = "' + flavor_id + '"'
            cur.execute(query)
            for row in cur.fetchall():
                return row[0]
        return None

    def get_hypervisors(self, hostname=None):
        """
        Return a dict containing the Hypervisors stored in Nova.
        If an hostname is given, it will return only the Hypervisor with the given hostname
        :param hostname: Optional hostname of the desired Hypervisor
        :return dict: contains Hypervisors information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:
            query = 'select * from compute_nodes where deleted = 0'
            if hostname:
                query += ' and hypervisor_hostname = "' + hostname + '"'
            cur.execute(query)
            for row in cur.fetchall():
                res[row[3]] = {}
                res[row[3]]['attributes'] = {}
                res[row[3]]['type'] = 'hypervisor'
                res[row[3]]['category'] = 'compute'
                res[row[3]]['resource_type'] = 'service'
                res[row[3]]['name'] = row[11] + '_' + row[19]
                hostname = row[19]
                if '.' in row[19]:
                    hostname = row[19].split('.')[0]
                res[row[3]]['hostname'] = hostname
                res[row[3]]['attributes']['service_id'] = row[4]
                res[row[3]]['attributes']['vcpus'] = row[5]
                res[row[3]]['attributes']['memory_mb'] = row[6]
                res[row[3]]['attributes']['local_gb'] = row[7]
                res[row[3]]['attributes']['vcpus_used'] = row[8]
                res[row[3]]['attributes']['memory_mb_used'] = row[9]
                res[row[3]]['attributes']['local_gb_used'] = row[10]
                res[row[3]]['attributes']['hypervisor_type'] = row[11]
                res[row[3]]['attributes']['hypervisor_version'] = row[12]
                res[row[3]]['attributes']['cpu_info'] = json.loads(row[13])
                res[row[3]]['attributes']['disk_available_least'] = row[14]
                res[row[3]]['attributes']['free_ram_mb'] = row[15]
                res[row[3]]['attributes']['free_disk_gb'] = row[16]
                res[row[3]]['attributes']['current_workload'] = row[17]
                res[row[3]]['attributes']['running_vms'] = row[18]
                res[row[3]]['attributes']['host_ip'] = row[21]
                res[row[3]]['attributes']['supported_instances'] = json.loads(row[22])
                res[row[3]]['attributes']['pci_stats'] = json.loads(row[23])
                res[row[3]]['attributes']['stats'] = json.loads(row[26])
                res[row[3]]['attributes']['numa_topology'] = json.loads(row[27])
        return res

    def get_instance_type(self, controller_hostname, uuid=None):
        """
        Return a dict containing the Instance Types stored in Nova.
        If an UUID is given, it will return only the Instance Type with the given UUID
        :param controller_hostname: Hostname of the OpenStack Controller
        :param uuid: Optional UUID of the desired Instance Type
        :return dict: Contains the instance types information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:
            query = 'SELECT * FROM instance_types where deleted = 0'

            if uuid:
                query += ' and flavorid = "' + uuid + '"'

            cur.execute(query)
            for row in cur.fetchall():
                res[row[9]] = {}
                res[row[9]]['attributes'] = {}
                res[row[9]]['type'] = 'flavor'
                res[row[9]]['resource_type'] = 'virtual'
                res[row[9]]['name'] = row[3]
                res[row[9]]['hostname'] = controller_hostname
                res[row[9]]['attributes']['memory_mb'] = row[5]
                res[row[9]]['attributes']['vcpus'] = row[6]
                res[row[9]]['attributes']['swap'] = row[7]
                res[row[9]]['attributes']['vcpu_weight'] = row[8]
                res[row[9]]['attributes']['rxtx_factor'] = row[10]
                res[row[9]]['attributes']['root_gb'] = row[11]
                res[row[9]]['attributes']['ephemeral_gb'] = row[12]
                res[row[9]]['attributes']['disabled'] = row[13]
                res[row[9]]['attributes']['is_public'] = row[14]
        return res

    def get_vm_per_host(self, hostname):
        """
        Return a list of VMs running on the machine specified by the hostname
        :param hostname: Hostname of the machine
        :return list: contains VMs information
        """
        res = []
        with closing(self.conn.cursor()) as cur:
            cur.execute('SELECT * FROM instances WHERE host="' + hostname + '"')
            for row in cur.fetchall():
                res.append(row)
        return res

    def pci_devices(self, compute_node_id):
        """
        Return list of PCI devices exposed by the compute node specified by id
        :param compute_node_id: ID of the compute node
        :return list: Contains PCI devices information
        """
        res = []
        with closing(self.conn.cursor()) as cur:
            cur.execute('SELECT * FROM pci_devices WHERE compute_node_id = ' + compute_node_id)
            for row in cur.fetchall():
                res.append(row)
        return res

    def key_pairs(self):
        """
        Return list of keypairs stored in Nova DB
        :return list: contains keypairs information
        """

        res = []
        with closing(self.conn.cursor()) as cur:
            cur.execute('SELECT * FROM key_pairs')
            for row in cur.fetchall():
                res.append(row)
        return res

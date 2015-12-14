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

# MAP driver name to Neutron agent name
MAP_DRIVER_BINARY = {
    'openvswitch': 'neutron-openvswitch-agent'
}


class NeutronDb():
    """
    Exposes methods to get information regarding Neutron resources.
    It manages the connection to the Neutron DB.
    """
    def __init__(self, host, usr, pwd, db):
        self.conn = None
        self.conn = MySQLdb.connect(host=host,
                                    user=usr,
                                    passwd=pwd,
                                    db=db)

    def get_routers(self, uuid=None):
        """
        Return a dict containing the routers stored in Glance.
        If an UUID is given, it will return only the router with the given UUID
        :param uuid: Optional UUID of the desired router
        :return dict: contains routers information
        """
        res = {}

        with closing(self.conn.cursor()) as cur:
            query = 'select * from routers left join ' \
                'routerl3agentbindings on routers.id = routerl3agentbindings.router_id'

            if uuid:
                query += ' where routers.id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[1]] = {}
                res[row[1]]['attributes'] = {}

                res[row[1]]['name'] = row[2]
                res[row[1]]['type'] = 'router'
                res[row[1]]['resource_type'] = 'virtual'
                res[row[1]]['category'] = 'network'
                res[row[1]]['attributes']['status'] = row[3]
                res[row[1]]['attributes']['admin_state_up'] = row[4]
                res[row[1]]['attributes']['gw_port_id'] = row[5]
                res[row[1]]['attributes']['enable_snat'] = row[6]
                res[row[1]]['attributes']['l3_agent_id'] = row[8]
                res[row[1]]['attributes']['ports'] = []
                port_query = 'select * from routerports where router_id="' + row[1] + '"'
                cur.execute(port_query)
                for port_row in cur.fetchall():
                    res[row[1]]['attributes']['ports'].append(port_row[1])

        return res

    def get_floating_ips(self, uuid=None):
        """
        Return a dict containing the FloatingIPs stored in Neutron.
        If an UUID is given, it will return only the FloatingIP with the given UUID
        :param uuid: Optional UUID of the desired FloatingIP
        :return dict: contains FloatingIPs information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:
            query = 'select * from floatingips'
            if uuid:
                query += ' where id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[1]] = {}
                res[row[1]]['attributes'] = {}
                res[row[1]]['type'] = 'floatingip'
                res[row[1]]['resource_type'] = 'virtual'
                res[row[1]]['category'] = 'network'
                res[row[1]]['attributes']['floating_ip_address'] = row[2]
                res[row[1]]['attributes']['network_id'] = row[3]
                res[row[1]]['attributes']['port_id'] = row[4]
                res[row[1]]['attributes']['fixed_port_id'] = row[5]
                res[row[1]]['attributes']['router_id'] = row[7]
                sub_query = 'select mac_address from ports where id = "' + row[4] + '" '
                cur.execute(sub_query)
                for sub_row in cur.fetchall():
                    res[row[1]]['attributes']['mac_address'] = sub_row[0]
                sub_query = 'select subnet_id from ipallocations where port_id = "' + row[4] + '" '
                cur.execute(sub_query)
                for sub_row in cur.fetchall():
                    res[row[1]]['attributes']['subnet_id'] = sub_row[0]
        return res

    def get_ports_by_instance_uuid(self, instance_uuid):
        """
        Return list of Neutron ports of the given nova instance.
        :param instance_uuid: UUID of the Nova Instance
        :return list: contains ports UUID
        """
        res = []
        cur = self.conn.cursor()
        query = 'SELECT id FROM ports WHERE device_id = "' + instance_uuid + '"'
        cur.execute(query)
        for row in cur.fetchall():
            res.append(row[0])
        return res

    def get_ports(self, uuid=None):
        """
        Return a dict containing the ports stored in Neutron.
        If an UUID is given, it will return only the port with the given UUID
        :param uuid: Optional UUID of the desired port
        :return dict: contains ports information
        """
        res = {}

        with closing(self.conn.cursor()) as cur:
            query = 'select * from ports where device_owner != "network:floatingip"'
            if uuid:
                query += ' and id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[1]] = {}
                res[row[1]]['attributes'] = {}

                if row[2] != '':
                    res[row[1]]['name'] = row[2]

                res[row[1]]['type'] = 'port'
                res[row[1]]['resource_type'] = 'virtual'
                res[row[1]]['category'] = 'network'
                res[row[1]]['attributes']['network_id'] = row[3]
                res[row[1]]['attributes']['mac_address'] = row[4]
                res[row[1]]['attributes']['admin_state_up'] = row[5]
                res[row[1]]['attributes']['status'] = row[6]
                res[row[1]]['attributes']['device_id'] = row[7]

                if row[8] != '':
                    res[row[1]]['attributes']['device_owner'] = row[8]

            query = 'select * from  ml2_port_bindings'

            cur.execute(query)

            for row in cur.fetchall():
                if row[0] in res.keys():
                    if row[1] != '':
                        res[row[0]]['hostname'] = row[1]
                    res[row[0]]['attributes']['vif_type'] = row[2]
                    res[row[0]]['attributes']['driver'] = row[3]
                    res[row[0]]['attributes']['segment'] = row[4]
                    res[row[0]]['attributes']['vnic_type'] = row[5]

                    if row[6] != '':
                        res[row[0]]['attributes']['vif_details'] = json.loads(row[6])
                    if row[7] != '':
                        res[row[0]]['attributes']['profile'] = row[7]

            query = 'select * from ipallocations'
            cur.execute(query)

            for row in cur.fetchall():
                if row[0] in res.keys():
                    res[row[0]]['attributes']['ip_address'] = row[1]
                    res[row[0]]['attributes']['subnet_id'] = row[2]

            for port in res.keys():
                if res[port]['attributes']['vif_type'] != 'unbound':
                    host = res[port]['hostname']
                    if res[port]['attributes']['driver'] in MAP_DRIVER_BINARY.keys():
                        driver = res[port]['attributes']['driver']
                        query = 'select id from agents where agents.host="' + host + \
                                '" and agents.binary="' + MAP_DRIVER_BINARY[driver] + '" LIMIT 1;'
                        cur.execute(query)
                        for row in cur.fetchall():
                            res[port]['attributes']['agent_id'] = row[0]

            query = 'select * from floatingips'

            cur.execute(query)

            for row in cur.fetchall():
                if row[5] in res.keys():
                    if 'floatingips' not in res[row[5]]['attributes'].keys():
                        res[row[5]]['attributes']['floatingips'] = []
                    res[row[5]]['attributes']['floatingips'].append(row[1])

        return res

    def get_agents(self, uuid=None):
        """
        Return a dict containing the Neutron agents stored in Neutron.
        If an UUID is given, it will return only the agent with the given UUID
        :param uuid: Optional UUID of the desired agent
        :return dict: contains agents information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select * from agents'

            if uuid:
                query += ' where id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['resource_type'] = 'service'
                res[row[0]]['name'] = row[1]
                res[row[0]]['hostname'] = row[4]
                res[row[0]]['category'] = 'network'
                res[row[0]]['type'] = row[2]
                res[row[0]]['attributes'] = {}
                res[row[0]]['attributes']['admin_state_up'] = row[5]
                res[row[0]]['attributes']['configurations'] = json.loads(row[10])
        return res

    def get_networks(self, uuid=None):
        """
        Return a dict containing the networks stored in Neutron.
        If an UUID is given, it will return only the network with the given UUID
        :param uuid: Optional UUID of the desired network
        :return dict: contains networks information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select n.id, n.name, n.status, n.admin_state_up, n.shared from networks n'

            if uuid:
                query += ' where n.id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[0]] = {}
                res[row[0]]['resource_type'] = 'virtual'
                res[row[0]]['name'] = row[1]
                res[row[0]]['type'] = 'net'
                res[row[0]]['category'] = 'network'
                res[row[0]]['attributes'] = {}
                res[row[0]]['attributes']['status'] = row[2]
                res[row[0]]['attributes']['admin_state_up'] = row[3]
                res[row[0]]['attributes']['shared'] = row[4]
                subnets = self.get_subnets_by_net_id(row[0])
                if subnets and len(subnets) > 0:
                    res[row[0]]['attributes']['subnets'] = subnets

            query = 'select m.network_id, m.network_type, m.physical_network, ' \
                'm.segmentation_id, m.is_dynamic from ml2_network_segments m'

            if uuid:
                query += ' where m.network_id = "' + uuid + '"'

            cur.execute(query)
            for row in cur.fetchall():
                res[row[0]]['attributes']['network_type'] = row[1]
                res[row[0]]['attributes']['physical_network'] = row[2]
                res[row[0]]['attributes']['segmentation_id'] = row[3]
                res[row[0]]['attributes']['is_dynamic'] = row[4]

            query = 'select network_id, dhcp_agent_id from networkdhcpagentbindings'

            if uuid:
                query += ' where network_id = "' + uuid + '"'

            cur.execute(query)
            for row in cur.fetchall():
                res[row[0]]['attributes']['dhcp_agent_id'] = row[1]

        return res

    def get_subnets_by_net_id(self, net_id):
        """
        Return a dict containing the Subnets stored in Neutron for a given Network.

        :param net_id: UUID of the desired Network
        :return dict: contains subnets information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select * from subnets where network_id = "' + net_id + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[1]] = {}
                res[row[1]]['name'] = row[2]
                res[row[1]]['attributes'] = {}
                res[row[1]]['attributes']['ip_version'] = row[4]
                res[row[1]]['attributes']['cidr'] = row[5]
                res[row[1]]['attributes']['gateway_ip'] = row[6]
                res[row[1]]['attributes']['enable_dhcp'] = row[7]
                res[row[1]]['attributes']['shared'] = row[8]
                res[row[1]]['attributes']['ipv6_ra_mode'] = row[9]
                res[row[1]]['attributes']['ipv6_address_mode'] = row[10]
                dns_query = 'select * from dnsnameservers where subnet_id="' + row[1] + '"'
                res[row[1]]['attributes']['dns_name_servers'] = list()
                cur.execute(dns_query)
                for dns_row in cur.fetchall():
                    res[row[1]]['attributes']['dns_name_servers'].append(dns_row[0])
                routes_query = 'select * from subnetroutes where subnet_id="' + row[1] + '"'
                res[row[1]]['attributes']['host_routes'] = list()
                cur.execute(routes_query)
                for routes_row in cur.fetchall():
                    res[row[1]]['attributes']['host_routes'].append(
                        {
                            'destination': routes_row[0],
                            'nexthop': routes_row[1]
                        }
                    )

        return res

    def get_subnets(self, uuid=None):
        """
        Return a dict containing the Subnets stored in Neutron.
        If an UUID is given, it will return only the subnet with the given UUID
        :param uuid: Optional UUID of the desired subnet
        :return dict: contains subnets information
        """
        res = {}
        with closing(self.conn.cursor()) as cur:

            query = 'select * from subnets'

            if uuid:
                query += ' where id = "' + uuid + '"'

            cur.execute(query)

            for row in cur.fetchall():
                res[row[1]] = {}
                res[row[1]]['resource_type'] = 'virtual'
                res[row[1]]['name'] = row[2]
                res[row[1]]['type'] = 'subnet'
                res[row[1]]['category'] = 'network'
                res[row[1]]['attributes'] = {}
                res[row[1]]['attributes']['network_id'] = row[3]
                res[row[1]]['attributes']['ip_version'] = row[4]
                res[row[1]]['attributes']['cidr'] = row[5]
                res[row[1]]['attributes']['gateway_ip'] = row[6]
                res[row[1]]['attributes']['enable_dhcp'] = row[7]
                res[row[1]]['attributes']['shared'] = row[8]
                res[row[1]]['attributes']['ipv6_ra_mode'] = row[9]
                res[row[1]]['attributes']['ipv6_address_mode'] = row[10]
                dns_query = 'select * from dnsnameservers where subnet_id="' + row[1] + '"'
                res[row[1]]['attributes']['dns_name_servers'] = list()
                cur.execute(dns_query)
                for dns_row in cur.fetchall():
                    res[row[1]]['attributes']['dns_name_servers'].append(dns_row[0])
                routes_query = 'select * from subnetroutes where subnet_id="' + row[1] + '"'
                res[row[1]]['attributes']['host_routes'] = list()
                cur.execute(routes_query)
                for routes_row in cur.fetchall():
                    res[row[1]]['attributes']['host_routes'].append(
                        {
                            'destination': routes_row[0],
                            'nexthop': routes_row[1]
                        }
                    )

        return res

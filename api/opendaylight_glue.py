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
Module to extract information from OpenDaylight
"""

__author__ = 'vmriccobene, gpetralia'

from api.opendaylight_api_call import call_odl_api
from py2neo import neo4j
from common import neo4j_resources as neo_resource
from occi.exceptions import HTTPError
from api import epa_glue


def get_topology(odl_url, odl_usr, odl_pass):
    """
    Retrieve the network topology from OpenDayLight
    :param odl_url: Url Endpoint of OpenDaylight
    :param odl_usr: OpenDaylight User
    :param odl_pass: OpenDaylight Password
    :return dict: network topology
    """
    if odl_url.endswith('/'):
        odl_url = odl_url[:-1]
    topology_url = odl_url + '/network-topology:network-topology/'
    topology_json = call_odl_api(odl_usr, odl_pass, topology_url)
    return topology_json


def get_node_features(odl_url, odl_usr, odl_pass, node_id):
    """
    Retrieve node features from OpenDaylight
    :param odl_url: Url Endpoint of OpenDaylight
    :param odl_usr: OpenDaylight User
    :param odl_pass: OpenDaylight Password
    :param node_id: OpenFlow Node ID
    :return dict: Node features
    """
    if odl_url.endswith('/'):
        odl_url = odl_url[:-1]
    inventory_url = odl_url + '/opendaylight-inventory:nodes/node/'
    node_url = inventory_url + node_id
    topology_json = call_odl_api(odl_usr, odl_pass, node_url)
    return topology_json


def get_switches_ids(pop_url, pop_id):
    """
    Retrieve list of Physical Switches

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :return list: List of Physical Switches OpenFlow IDs
    """
    odl_info = _get_odl_info(pop_url, pop_id)
    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    results = []
    for topology in topology_json['network-topology']['topology']:
        nodes = topology['node']
        for node in nodes:
            node_features_json = get_node_features(odl_info[0], odl_info[1], odl_info[2], node['node-id'])
            if 'node' in node_features_json:
                for node_json in node_features_json['node']:
                    if 'flow-node-inventory:serial-number' in node_json \
                            and node_json['flow-node-inventory:serial-number'].strip() != 'None':
                        results.append(node['node-id'])
    return results


def get_switch_interfaces_by_switch_id(pop_url, pop_id, switch_id):
    """
    Retrieve Switch Interfaces controlled by OpenDaylight for a
    given Switch

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param switch_id: OpenFlow Switch ID
    :return list: List of OpenFlow IDs of switch's Interfaces
    """
    odl_info = _get_odl_info(pop_url, pop_id)
    node_features_json = get_node_features(odl_info[0], odl_info[1], odl_info[2], switch_id)
    results = []
    if 'node' in node_features_json:
        for node_json in node_features_json['node']:
            if 'node-connector' in node_json:
                for connector in node_json['node-connector']:
                    results.append(connector['id'])
    return results


def _get_odl_info(pop_url, pop_id):
    """
    Retrieve OpenDaylight Url, username and password from the PoP DB

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :return tuple: (ODL url, ODL username, ODL password
    """
    try:
        graph_db = neo4j.Graph(pop_url)
        index = ('pop', 'uuid', pop_id)
        pop = neo_resource.get_node(graph_db, index)
        if pop:
            properties = dict(pop.properties)
            if 'occi.epa.pop.odl_url' in properties and 'occi.epa.pop.odl_name' in properties \
                    and 'occi.epa.pop.odl_password' in properties:
                return properties['occi.epa.pop.odl_url'], properties['occi.epa.pop.odl_name'],\
                    properties['occi.epa.pop.odl_password']

    except Exception:
        raise HTTPError(404, 'Error connecting to graph_url: ' + str(pop_url))
    raise HTTPError(404, 'Resource not found: Epa-Pop-Id: ' + str(pop_id))


def get_switch(pop_url, pop_id, switch_id):
    """
    Retrieve attributes of a given switch

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param switch_id: OpenFlow Switch ID
    :return dict: Switch properties
    """
    odl_info = _get_odl_info(pop_url, pop_id)

    node_features_json = get_node_features(odl_info[0], odl_info[1], odl_info[2], switch_id)
    result = {}
    if 'node' in node_features_json:
        for node_json in node_features_json['node']:
            result['name'] = node_json.get('flow-node-inventory:description', '')
            result['attributes'] = {}
            result['attributes']['software'] = node_json.get("flow-node-inventory:software", '')
            result['attributes']['hardware'] = node_json.get("flow-node-inventory:hardware", '')
            result['attributes']['ip-address'] = node_json.get("flow-node-inventory:ip-address", '')
            result['attributes']['serial-number'] = node_json.get("flow-node-inventory:serial-number", '')
            result['attributes']['manufacturer'] = node_json.get("flow-node-inventory:manufacturer", '')
            result['attributes']['switch-features'] = node_json.get("flow-node-inventory:switch-features", '')
            return result


def get_switch_interfaces(pop_url, pop_id):
    """
    Retrieve all the switch interfaces controlled by OpenDaylight

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :return list: List of switch interface OpenFlow IDs
    """
    odl_info = _get_odl_info(pop_url, pop_id)
    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    results = []
    for topology in topology_json['network-topology']['topology']:
        nodes = topology['node']
        for node in nodes:
            node_features_json = get_node_features(odl_info[0], odl_info[1], odl_info[2], node['node-id'])
            if 'node' in node_features_json:
                for node_json in node_features_json['node']:
                    if 'flow-node-inventory:serial-number' in node_json \
                            and node_json['flow-node-inventory:serial-number'].strip() != 'None':
                        if 'node-connector' in node_json:
                            for connector in node_json['node-connector']:
                                results.append(connector['id'])
    return results


def get_switch_interface(pop_url, pop_id, uuid):
    """
    Retrieve attributes for a given Switch Interface

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param uuid: OpenFlow Switch ID
    :return dict: Attributes of the switch interface
    """
    odl_info = _get_odl_info(pop_url, pop_id)
    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    results = {}
    for topology in topology_json['network-topology']['topology']:
        nodes = topology['node']
        for node in nodes:
            node_features_json = get_node_features(odl_info[0], odl_info[1], odl_info[2], node['node-id'])
            if 'node' in node_features_json:
                for node_json in node_features_json['node']:
                    if 'flow-node-inventory:serial-number' in node_json \
                            and node_json['flow-node-inventory:serial-number'].strip() != 'None':
                        if 'node-connector' in node_json:
                            for connector in node_json['node-connector']:
                                if connector['id'] == uuid:
                                    results['name'] = connector.get('flow-node-inventory:name', '')
                                    results['attributes'] = {}
                                    results['attributes']['port-number'] = \
                                        connector.get('flow-node-inventory:port-number', '')
                                    results['attributes']['current-speed'] = \
                                        connector.get('flow-node-inventory:current-speed', '')
                                    results['attributes']['flow-capable-node-connector-statistics'] = \
                                        connector.get(
                                            'opendaylight-port-statistics:flow-capable-node-connector-statistics', '')
                                    results['attributes']['advertised-features'] = \
                                        connector.get('flow-node-inventory:advertised-features', '')
                                    results['attributes']['configuration'] = \
                                        connector.get('flow-node-inventory:configuration', '')
                                    results['attributes']['hardware-address'] = \
                                        connector.get('flow-node-inventory:hardware-address', '')
                                    results['attributes']['maximum-speed'] = \
                                        connector.get('flow-node-inventory:maximum-speed', '')
                                    results['attributes']['state'] = \
                                        connector.get('flow-node-inventory:state', '')
                                    results['attributes']['supported'] = \
                                        connector.get('flow-node-inventory:supported', '')
                                    results['attributes']['current-feature'] = \
                                        connector.get('flow-node-inventory:current-feature', '')
                                    results['attributes']['peer-features'] = \
                                        connector.get('flow-node-inventory:peer-features', '')
                                    return results


def get_switch_by_interface(pop_url, pop_id, uuid):
    """
    Retrieve switch ID of a given interface

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param uuid: OpenFlow Switch Interface ID
    :return string: OpenFlow Switch ID
    """

    odl_info = _get_odl_info(pop_url, pop_id)
    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    for topology in topology_json['network-topology']['topology']:
        nodes = topology['node']
        for node in nodes:
            node_features_json = get_node_features(odl_info[0],
                                                   odl_info[1],
                                                   odl_info[2],
                                                   node['node-id'])
            if 'node' in node_features_json:
                for node_json in node_features_json['node']:
                    if 'flow-node-inventory:serial-number' in node_json \
                            and node_json['flow-node-inventory:serial-number'].strip() != 'None':
                        if 'node-connector' in node_json:
                            for connector in node_json['node-connector']:
                                if connector['id'] == uuid:
                                    switch_uuid = node['node-id']
                                    return switch_uuid


def get_os_dev_by_switch_interface(pop_url, pop_id, uuid):
    """
    Retrieve the ID of the OS device connected to the given
    Switch Interface. None if there is no OS device connected

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param uuid: Switch Interface OpenFlow ID
    :return string: OS Device ID
    """
    odl_info = _get_odl_info(pop_url, pop_id)

    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    for topology in topology_json['network-topology']['topology']:
        if 'link' in topology:
            for link in topology['link']:
                if link['source']['source-tp'] == uuid:
                    mac = link['destination']['dest-node'].split('host:')[1]
                    os_dev = epa_glue.get_os_dev_by_mac(pop_url, pop_id, mac)
                    return os_dev


def get_switch_interface_by_mac(pop_url, pop_id, mac):
    """
    Retrieve the Switch Interface ID of the Switch Interface
    connected to the OS Device having the given MAC Address

    :param pop_url: Url of Neo4j PoP DB
    :param pop_id: PoP ID
    :param mac: OS Device MAC address
    :return string: Switch Interface OpenFlow ID
    """

    switches = get_switches_ids(pop_url, pop_id)
    odl_info = _get_odl_info(pop_url, pop_id)
    topology_json = get_topology(odl_info[0], odl_info[1], odl_info[2])
    for topology in topology_json['network-topology']['topology']:
        if 'link' in topology:
            for link in topology['link']:
                if mac in link['source']['source-tp']:
                    destination = link['destination']['dest-tp']
                    split_destination = destination.split(':')
                    if len(split_destination) == 3:
                        switch_id = split_destination[0] + ':' + split_destination[1]
                        if switch_id in switches:
                            return destination

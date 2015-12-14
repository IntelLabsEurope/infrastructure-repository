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
Module to manage Hw information of a node.
It takes in input the files produced by the agents,
parses them and it stores a graph representation of the host
in Neo4j
"""

__author__ = 'gpetralia'

import xml.etree.ElementTree as Et
import time
import json

import networkx as nx

import common.neo4j_resources as neo_resource


# Map numerical types used by hardware locality to string categories
OSDEVTYPE_CATEGORY_MAP = {
    '0': 'storage',  # HWLOC_OBJ_OSDEV_BLOCK
    '1': 'compute',  # HWLOC_OBJ_OSDEV_GPU
    '2': 'network',  # HWLOC_OBJ_OSDEV_NETWORK
    '3': 'network',  # HWLOC_OBJ_OSDEV_OPENFABRICS
    '4': 'compute',  # HWLOC_OBJ_OSDEV_DMA
    '5': 'compute',  # HWLOC_OBJ_OSDEV_COPROC
}


class HostHwResources(object):
    """
    Class to manage hw resources in the Neo4j DB
    """
    def __init__(self, hostname, pop_id, graph_db):
        self.hostname = hostname
        self.graph_db = graph_db
        self.pop_id = pop_id
        self.label = 'physical_resource'
        self.index = 'physical_name'

    def store(self, path, hwloc_file, cpu_file=None, sriov_file=None, dpdk_file=None, timestamp=None):
        """
        Store information contained in files created by the EPA agents into Neo4j.
        using a networkx graph
        :param path: Path of the files
        :param hwloc_file: Hardware locality file
        :param cpu_file: Optional cpu information file
        :param sriov_file: Optional SR-IOV information file
        :param dpdk_file: Optional DPDK information file
        :param timestamp: Optional timestamp in epoch
        """
        graph = nx.DiGraph()
        xml_root = Et.parse(path + hwloc_file).getroot()
        deleted_edges = {}
        for child in xml_root:
            _parse_object_hwloc(graph, child, self.hostname, deleted_edges, self.pop_id)

        if cpu_file is not None:
            processors_dict = _parse_cpu_info(path + cpu_file)
            _enrich_graph_cpuinfo(graph, processors_dict)

        if dpdk_file is not None:
            dpdk_dict = _parse_dpdk_info(path + dpdk_file)
            _enrich_graph_dpdkinfo(graph, dpdk_dict)

        if sriov_file is not None:
            sriov_dict = _parse_sriov_info(path + sriov_file)
            _enrich_graph_sriovinfo(graph, sriov_dict)

        if timestamp is not None:
            now = timestamp
        else:
            now = time.time()

        neo_id_nodes = {}

        nodes_to_add = []
        nodes_stored = []

        query_string = 'Match n Where n.hostname = {hostname} ' \
                       'And n.resource_type = {resource_type} Return n.physical_name'

        res = self.graph_db.cypher.execute(query_string, hostname=self.hostname, resource_type='physical')

        for item in res:
            print str(item)
            nodes_stored.append(item['n.physical_name'])

        for nx_node in graph.nodes():
            nodes_to_add.append(str(nx_node))
            neo_id_nodes[nx_node] = neo_resource.add_node(self.graph_db, (self.label, self.index, nx_node), now,
                                                          get_node_properties(graph, nx_node))

        nodes_to_remove = [item for item in nodes_stored if item not in nodes_to_add]

        for node in nodes_to_remove:
            neo_resource.delete_node(self.graph_db, (self.label, self.index, node))

        for edge in graph.edges():
            source = edge[0]
            target = edge[1]
            edge_label = ''
            if 'label' in graph.edge[source][target]:
                edge_label = graph.edge[source][target]['label']
            db_src = neo_id_nodes[source]
            db_target = neo_id_nodes[target]
            rel_stored = neo_resource.get_edge(self.graph_db, db_src, db_target)
            if rel_stored is None:
                neo_resource.add_edge(self.graph_db, db_src, db_target, timestamp, edge_label)
            else:
                neo_resource.update_edge(self.graph_db, timestamp, edge_label, db_src=db_src, db_target=db_target)


def get_node_properties(graph, node_name):
    """
    Return a dict containing nodes properties
    :param graph: Networkx graph
    :param node_name: name of the node
    :return dict: Node properties
    """
    neo_node = {}

    for item in graph.node[str(node_name)]:

        if isinstance((graph.node[str(node_name)][item]), dict):
            neo_node[item] = json.dumps(graph.node[str(node_name)][item])
        else:
            neo_node[item] = str(graph.node[str(node_name)][item])

    neo_node['physical_name'] = node_name
    return neo_node


def _enrich_graph_sriovinfo(graph, sriov_dict):
    """
    Enrich the graph with SR-IOV information
    :param graph: networkx graph
    :param sriov_dict: SR-IOV information
    """
    for node, attr in graph.nodes(data=True):
        if 'pci_busid' in attr['attributes'].keys() and attr['attributes']['pci_busid'] in sriov_dict.keys():
            attr['attributes']['sriov'] = sriov_dict[attr['attributes']['pci_busid']]


def _enrich_graph_dpdkinfo(graph, dpdk_dict):
    """
    Enrich the graph with DPDK information
    :param graph: networkx graph
    :param dpdk_dict: DPDK information
    """
    for node, attr in graph.nodes(data=True):
        if 'pci_busid' in attr['attributes'].keys() and attr['attributes']['pci_busid'] in dpdk_dict.keys():
            attr['attributes']['dpdk'] = True


def _enrich_graph_cpuinfo(graph, processors_dict):
    """
    Navigate the graph and
    add attributes from processor_list
    to the PU nodes.

    The key between processor_list and hwlock_graph
    is the os_index attribute.

    :param graph: the graph that should be enriched
    :param processors_dict: a dict of cpu attributes
    """
    for node, attr in graph.nodes(data=True):
        if '_PU_' in node:
            index = int(attr['attributes']['os_index'])
            attr['attributes'].update(processors_dict[index])


def _parse_sriov_info(sriov_info_file):
    """
    Create a dict containing information extracted from the SR-IOV file
    :param sriov_info_file: SR-IOV file
    :return dict: SR-IOV information
    """
    sriov_dict = {}
    with open(sriov_info_file) as f:
        for line in f:
            line = sanitize_string(line)
            attr = line.split(' ')
            if len(attr) == 3:
                sriov_dict[attr[0]] = {"numvfs": attr[1], "totalvfs": attr[2]}

    return sriov_dict


def _parse_dpdk_info(dpdk_info_file):
    """
    Create a dict containing information extracted from the DPDK file
    :param dpdk_info_file: DPDK file
    :return dict: DPDK information
    """
    dpdk_dict = {}
    with open(dpdk_info_file) as f:
        for line in f:
            line = sanitize_string(line)
            dpdk_dict[line] = {"dpdk": True}

    return dpdk_dict


def _parse_cpu_info(cpu_info_file):
    """
    Parse the text cpuinfo file
    and create a dict of processors.
    Each processor is a dict with all the attributes given by cpuinfo.

    :param cpu_info_file: Text file with the output of cat /proc/cpuinfo
    :return processors_dict: Dictionary containing attributes of each proc
    """
    processors_dict = {}

    with open(cpu_info_file) as f:
        current_id = None
        for line in f:
            attr = line.split(':')

            if len(attr) > 1:
                attr[0] = sanitize_string(attr[0])
                attr[1] = sanitize_string(attr[1])

                if 'processor' in attr[0]:
                    current_id = int(attr[1])
                    processors_dict[current_id] = {}
                    processors_dict[current_id]['id'] = attr[1]
                elif current_id is not None and attr[1] is not None and attr[1] is not '':
                    processors_dict[current_id][attr[0]] = attr[1]

    return processors_dict


def _parse_object_hwloc(graph, obj, host_name, deleted_edges, pop_id, parent=None):
    """
    Given an xml object extracted from Hardware locality file, create the
    corresponding node in the Networkx graph

    :param graph: netowrkx graph
    :param obj: xml object
    :param host_name: hostname of the host who the hwloc obj belongs to
    :param deleted_edges: list of edges to delete
    :param pop_id: PoP ID
    :param parent: Optional reference to the parent of the current object
    """
    object_children = []
    new_node_properties = {
        'resource_type': 'physical',
        'category': _get_category(obj),
        'type': obj.attrib['type'],
        'hostname': host_name,
        'pop': pop_id,
        'attributes': _get_attributes(obj)
    }

    node_name = _get_unique_name(obj, host_name)

    attr = obj.attrib.copy()
    del attr['type']

    # Saving the children to be parsed
    for child in obj:
        if child.tag == 'object':
            object_children.append(child)

    graph.add_node(node_name, attr_dict=new_node_properties)

    # Adding the edge between current node and the parent
    if parent is not None:
        graph.add_edge(parent, node_name, label='INTERNAL')
        if parent in deleted_edges.keys():
            graph.add_edge(deleted_edges[parent], node_name, label='INTERNAL')

    # Resolving the bug of hwloc that shows
    # the 2 caches L1 (data and instruction)
    # as they are one under the other
    if parent is not None:
        if new_node_properties['type'] == 'Cache':
            parent_type = ''
            parent_depth = ''
            for node, node_attr in graph.nodes(data=True):
                if node == parent:
                    parent_type = node_attr['type']
                    if parent_type == 'Cache':
                        parent_depth = node_attr['attributes']['depth']

            if parent_type == new_node_properties['type'] and attr['depth'] == parent_depth:
                graph.remove_edge(parent, node_name)
                deleted_edges[node_name] = parent
                parent = graph.pred[parent].keys()[0]
                graph.add_edge(parent, node_name, label='INTERNAL')

    # Recursively calls the function to parse the child of current node
    for obj in object_children:
        _parse_object_hwloc(graph, obj, host_name, deleted_edges, pop_id, parent=node_name)


def _get_category(hw_obj):
    """
    Given an object from the hwloc xml file
    the function return the category of the node
    choosen using the OSDETYPE_CATEGORY_MAP

    :param hw_obj: object extracted from hwloc xml file
    :rtype string
    :return: category
    """
    attrib = hw_obj.attrib

    if 'osdev_type' in attrib.keys():
        category = OSDEVTYPE_CATEGORY_MAP[attrib['osdev_type']]
    else:
        category = 'compute'

    return category


def _get_attributes(hw_obj):
    """
    Return a dict containing the attributes
    of an xml object extracted from Hwloc xml file
    :param hw_obj: hw object to be parsed
    :return dict: attributes of the object
    """
    attributes = hw_obj.attrib.copy()

    del attributes['type']

    for child in hw_obj:
        if child.tag == 'info':
            name = child.attrib['name']
            value = child.attrib['value']
            attributes[name] = value

    return attributes


def _get_unique_name(hw_obj, hostname):
    # UniqueName
    # Cache: hostname_Cache_[cpuset]_[depth]_[cache_type]
    # OSDev: hostname_OSDev_[name]
    # otherwise: hostname_[type]_os_index

    obj_type = hw_obj.attrib['type']

    if obj_type == 'Cache':
        return hostname + '_' + 'Cache' + '_' + hw_obj.attrib['cpuset'] + '_' + hw_obj.attrib['depth'] + '_' + \
            hw_obj.attrib['cache_type']

    if obj_type == 'OSDev':
        return hostname + '_' + 'OSDev' + '_' + hw_obj.attrib['name']

    if obj_type == 'Core':
        print "Core"
        return hostname + '_' + 'Core' + '_' + hw_obj.attrib['cpuset']

    return hostname + '_' + hw_obj.attrib['type'] + '_' + hw_obj.attrib['os_index']


def sanitize_string(input_string, space=True):
    """
    Sanitize the input_string changing it to lowercase,
    deleting space at the start and at the end

    :param input_string:
    :param space: if space=False, spaces will be replaced with _
    :return:
    """
    output_string = input_string.strip().lower().replace('-', '_').replace('\n', '')
    if not space:
        output_string = output_string.replace(' ', '_')
    return output_string

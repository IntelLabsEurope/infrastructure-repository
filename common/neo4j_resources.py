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
Managing single resources in neo4j

"""

__author__ = 'gpetralia'

from py2neo import Relationship
import json


def create_index(graph_db, index):
    """
    Create index in neo4j
    :param graph_db: Graph db instance
    :param index: tuple containing (label, property key for UUID, UUID)
    """
    index_created = False
    if index and len(index) > 1:
        for i in graph_db.schema.get_indexes(index[0]):
            if i == index[1]:
                index_created = True

        if not index_created:
            graph_db.schema.create_index(index[0], index[1])


def add_node(graph_db, index, timestamp, properties=None):
    """
    Add a new node

    :param graph_db: Graph db instance
    :param index: tuple containing (label, property key for UUID, UUID)
    :param timestamp: timestamp in epoch
    :param properties: dict containing node's properties
    :return Node: created node
    """

    create_index(graph_db, index)
    neo_properties = dict()
    neo_properties['index_type'] = index[0]
    neo_properties[index[1]] = index[2]
    if properties is not None:
        for key in properties:
            if isinstance(properties[key], dict):
                neo_properties[key] = json.dumps(properties[key])
            else:
                neo_properties[key] = str(properties[key])

    neo_properties['timestamp'] = timestamp

    node = graph_db.merge_one(index[0], index[1], index[2])
    node.properties.update(neo_properties)
    graph_db.push(node)
    return node


def update_node(graph_db, index, timestamp, properties=None):
    """
    Update an existing node

    :param graph_db: Graph db instance
    :param index: tuple containing (label, property key for UUID, UUID)
    :param timestamp: timestamp in epoch
    :param properties: optional dict containing node's properties
    :return Node: updated node
    """
    node = None
    neo_properties = dict()
    neo_properties[index[1]] = index[2]
    if properties is not None:
        for key in properties:
            if isinstance(properties[key], dict):
                neo_properties[key] = json.dumps(properties[key])
            else:
                neo_properties[key] = str(properties[key])

        neo_properties['timestamp'] = timestamp

        node = graph_db.find_one(index[0], property_key=index[1], property_value=index[2])
        if node:
            node.properties.update(neo_properties)
            graph_db.push(node)
    return node


def delete_node(graph_db, index=None, node=None):
    """
    Delete a given node specified by index or reference
    :param graph_db: Graph db instance
    :param index: optional node index
    :param node:  optional node reference
    :return Node: deleted node
    """
    if not node:
        node = get_node(graph_db, index)
    if node:
        edges = get_edges_by_node(graph_db, node=node)
        edges.append(node)
        graph_db.delete(*edges)
    return node


def add_edge(graph_db, db_src, db_target, timestamp, label, properties=None):
    """
    Add a relation between two nodes

    :param graph_db: Graph db instance
    :param db_src: source of the relation
    :param db_target: target of the relation
    :param timestamp: timestamp in epoch
    :param label: label of the relation
    :param properties: optional properties of the
    :return Relation: created relation
    """
    if not properties:
        properties = dict()

    if db_src and db_target:
        edge = graph_db.match_one(start_node=db_src, end_node=db_target)
        properties['timestamp'] = timestamp
        if edge is None:
            edge = Relationship.cast(db_src, label, db_target, properties)
            graph_db.create(edge)
        else:
            edge = update_edge(graph_db, timestamp, label, edge=edge)
        return edge


def delete_edge(graph_db, db_src, db_target):
    """
    Delete existing edge
    :param graph_db:  Graph db instance
    :param db_src: Source of the relation
    :param db_target: Target of the relation
    """
    edge = graph_db.match_one(start_node=db_src, end_node=db_target)
    if edge:
        graph_db.delete(edge)


def update_edge(graph_db, timestamp, label, db_src=None, db_target=None, edge=None, properties=None):
    """
    Update a Relation given source and target or Relation reference
    :param graph_db: Graph db instance
    :param timestamp: timestamp in epoch
    :param label: new label of the relation
    :param db_src: optional source of the relation
    :param db_target: optional target of the relation
    :param edge: optional reference of the relation
    :param properties: optional properties of the relation
    :return Relation: updated relation
    """
    if not properties:
        properties = dict()
    if not edge and db_src and db_target:
        edge = graph_db.match_one(start_node=db_src, end_node=db_target)
    properties['timestamp'] = timestamp
    if edge:
        edge.properties.update(properties)
        edge.labels = [label]
        graph_db.push(edge)
    return edge


def get_edges_by_node(graph_db, node=None, index=None):
    """
    Get all the relation of a node
    specified by index or by refernce
    :param graph_db: Graph DB reference
    :param node: optional node reference
    :param index: optional index
    :return list: list of relations
    """
    edges = list()
    if not node and index:
        node = get_node(graph_db, index)
    if node:
        edges = [r for r in node.match()]
    return edges


def get_neighbours(graph_db, node=None, index=None):
    """
    Return nodes connected to the given one

    :param graph_db: Graph DB reference
    :param node: optional node reference
    :param index: optional index
    :return list: list of connected nodes
    """
    neighbours = list()
    if not node and index:
        node = get_node(graph_db, index)
    if node:
        in_edges = [r for r in node.match_incoming()]
        for edge in in_edges:
            neighbours.append(edge.start_node)
        out_edges = [r for r in node.match_outgoing()]
        for edge in out_edges:
            neighbours.append(edge.end_node)
    return neighbours


def remove_neighbours(graph_db, node=None, index=None, neighbour_type=None):
    """
    Delete nodes connected to the given one
    :param graph_db: Graph DB reference
    :param node: optional node reference
    :param index: optional index
    :param neighbour_type: optional neighbours type used as filter
    """
    neighbours = get_neighbours(graph_db, node=node, index=index)

    for n in neighbours:
        if neighbour_type:
            if n.properties['type'] == neighbour_type:
                delete_node(graph_db, node=n)
        else:
            delete_node(graph_db, node=n)


def get_node(graph_db, index):
    """
    Get a node by index
    :param graph_db: Graph DB reference
    :param index: Index of the node
    :return Node: node reference
    """
    node = graph_db.find_one(index[0], property_key=index[1], property_value=index[2])
    return node


def get_node_by_property(graph_db, label, property_key, property_value):
    """
    Get first node with the given property
    :param graph_db: Graph DB reference
    :param label: label of the node
    :param property_key: property key of the node
    :param property_value: property value of the node
    :return Node: First node with the given property
    """
    node = graph_db.find_one(label, property_key=property_key, property_value=property_value)
    return node


def get_edge(graph_db, db_src, db_trg):
    """
    Get relation given source and target
    :param graph_db: Graph DB reference
    :param db_src: Source of the relation
    :param db_trg: Target of the relation
    :return Relation:
    """
    edge = graph_db.match_one(start_node=db_src, end_node=db_trg)
    return edge


def remove_nodes_by_property(graph_db, label, property_key, property_value):
    """
    Delete nodes with the given property

    :param graph_db: Graph DB reference
    :param label: label of the nodes
    :param property_key: property key of the nodes
    :param property_value: property value of the nodes
    """
    nodes = graph_db.find(label, property_key=property_key, property_value=property_value)
    for node in nodes:
        delete_node(graph_db, node=node)


def has_edge(graph_db, edge_type, dest_label, dest_property, dest_value, incoming=False, node=None, index=None):
    """
    Check if a node has a given relation

    :param graph_db: Graph DB instance
    :param edge_type: label of the edge
    :param dest_label: label of the destination
    :param dest_property: property key of the destination node
    :param dest_value: property value of the destination node
    :param incoming: Boolean to specify if the relation is inward or outward
    :param node: optional reference to the source node
    :param index: optional index of the source node
    :return tuple: (boolean, destination node)
    """
    if not node and index:
        node = get_node(graph_db, index)
    edges = None
    if node:
        if not incoming:
            edges = [r for r in node.match_outgoing()]
        else:
            edges = [r for r in node.match_incoming()]
    if edges:
        for edge in edges:
            if edge.type == edge_type:
                if not incoming:
                    dest_node = edge.end_node
                else:
                    dest_node = edge.start_node
                if dest_node and dest_label in dest_node.labels and dest_property in dest_node and \
                   dest_node[dest_property] == dest_value:
                    return True, dest_node

    return False, None


def get_nodes_by_attribute(graph_db, hostname, resource_type, attribute):
    """
    Get nodes by attribute and hostname

    :param graph_db: Graph DB instance
    :param hostname: hostname of the nodes
    :param resource_type: label of the nodes
    :param attribute: attribute value
    :return list: List of nodes
    """

    nodes = []
    query = 'match n where ' \
            'n.hostname="' + hostname + '" ' \
            'and n.type="' + resource_type + '"  ' \
            'and n.attributes=~".*' + attribute + '.*" ' \
            'return n'

    results = graph_db.cypher.execute(query)

    for res in results.records:
        nodes.append(res.n)

    return nodes

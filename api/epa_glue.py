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
Module to retrieve information from EPA Neo4j DB
"""

__author__ = 'gpetralia'

from py2neo import neo4j
from common import neo4j_resources as neo_resource
from occi.exceptions import HTTPError
from py2neo import Relationship
import json


def _get_physical_resource_by_type_and_uuid(graph_db, pop, resource_type, uuid):
    """
    Retrieve properties of a given physical node, given its type and
    its unique ID
    :param graph_db: Graph instance pointing to the EPA DB
    :param pop: PoP Name
    :param resource_type: Type of the resource
    :param uuid: Node uuid
    :return dict: Node properties
    """
    query = 'match node where node.type=~"(?i){}" and node.pop="{}" ' \
            'and node.physical_name = "{}" return node'.format(resource_type, pop, uuid)

    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url ")
    for record in data.records:
        node_properties = dict(record.node.properties)
        return node_properties

    raise HTTPError(404, 'Resource not found: /' + str(resource_type) + '/' + uuid)


def _get_resource_by_type_and_uuid(graph_db, pop, resource_type, uuid):
    """
    Retrieve properties of a given virtual node, given its type and
    its unique ID
    :param graph_db: Graph instance pointing to the EPA DB
    :param pop: PoP Name
    :param resource_type: Type of the resource
    :param uuid: Node uuid
    :return dict: Node properties
    """
    query = 'match node where node.type="{}" and node.pop="{}" ' \
            'and node.openstack_uuid = "{}" return node'.format(resource_type, pop, uuid)

    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url ")
    for record in data.records:
        node_properties = dict(record.node.properties)
        return node_properties

    raise HTTPError(404, 'Resource not found: /' + str(resource_type) + '/' + uuid)


def get_resource(pop_url, pop_id, resource_type, uuid, physical=False):
    """
    Retrieve properties of a given node and sanitize them given its type and
    its unique ID
    :param pop_url:  Url of PoP DB
    :param pop_id: PoP Name
    :param resource_type: Type of the resource
    :param uuid: Node uuid
    :param physical: Boolean default False.
    It is True if the node that should be retrieved is a physical node
    :return dict: Node properties
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)
    graph_db = neo4j.Graph(graph_url)
    if physical:
        node_properties = _get_physical_resource_by_type_and_uuid(graph_db, pop, resource_type, uuid)
    else:
        node_properties = _get_resource_by_type_and_uuid(graph_db, pop, resource_type, uuid)
    results = {}
    for key in node_properties:
        if isinstance(node_properties[key], str):
            results[key] = node_properties[key].strip().lower()
        else:
            results[key] = node_properties[key]
    return results


def get_link(pop_url, pop_id, source_uuid, target_uuid):
    """
    Retrieve Link information given source and target uuid
    :param pop_url: Url of PoP DB
    :param pop_id: PoP ID
    :param source_uuid: link's source uuid
    :param target_uuid: link's target uuid
    :return dict: It returns label and target type of the link
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)
    graph_db = neo4j.Graph(graph_url)
    query = 'match n-[r]->m where n.openstack_uuid="{}" and m.openstack_uuid="{}" ' \
            ' return r, m.type'.format(source_uuid, target_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        result = {
            'label': record.r.type.lower(),
            'target_type': record['m.type']
        }
        return result

    query = 'match n-[r]->m where n.openstack_uuid="{}" and m.physical_name="{}" ' \
            ' return r, m.type'.format(source_uuid, target_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        result = {
            'label': record.r.type.lower(),
            'target_type': record['m.type']
        }
        return result

    query = 'match n-[r]->m where n.physical_name="{}" and m.openstack_uuid="{}" ' \
            ' return r, m.type'.format(source_uuid, target_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        result = {
            'label': record.r.type.lower(),
            'target_type': record['m.type']
        }
        return result

    query = 'match n-[r]->m where n.physical_name="{}" and m.physical_name="{}" ' \
            ' return r, m.type'.format(source_uuid, target_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        result = {
            'label': record.r.type.lower(),
            'target_type': record['m.type']
        }
        return result


def get_links_target_uuid(pop_url, pop_id, source_uuid):
    """
    Retrieve Link target uuids given link's source uuid
    :param pop_url: Url of PoP DB
    :param pop_id: PoP ID
    :param source_uuid: link's source uuid
    :return list: List of link's targets UUIDs
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)

    graph_db = neo4j.Graph(graph_url)
    query = 'match n-[r]->m where n.openstack_uuid="{}" ' \
            ' return m'.format(source_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)
    results = []
    for record in data.records:
        m_properties = dict(record.m.properties)
        if 'openstack_uuid' in m_properties:
            results.append((m_properties['openstack_uuid'], m_properties['type'].lower()))

        if 'physical_name' in m_properties:
            results.append((m_properties['physical_name'], m_properties['type'].lower()))

    query = 'match n-[r]->m where n.physical_name="{}" ' \
            ' return m'.format(source_uuid)

    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        m_properties = dict(record.m.properties)
        if 'openstack_uuid' in m_properties:
            results.append((m_properties['openstack_uuid'], m_properties['type'].lower()))

        if 'physical_name' in m_properties:
            results.append((m_properties['physical_name'], m_properties['type'].lower()))

    return results


def get_resource_openstack_ids(pop_url, pop_id, resource_type, query_params=list()):
    """
    Retrive list of nodes uuid of a given type
    :param pop_url: Url of PoP DB
    :param pop_id: PoP ID
    :param resource_type: type of nodes that should be retrieved
    :param query_params: optional list of (key, value)s used as query parameters
    :return list: list of nodes uuids
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)

    query = 'match node where node.type="{}" and node.pop="{}" '.format(resource_type, pop)

    for q in query_params:
        if len(q[0]) > 0 and len(q[1]) > 0:
            val = '(?i).*%s.*' % (q[1])
            query += 'and node.attributes=~"{}"'.format(val)

    query += ' return node.openstack_uuid'
    graph_db = neo4j.Graph(graph_url)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)
    results = []
    for record in data.records:
        if record['node.openstack_uuid']:
            results.append(record['node.openstack_uuid'])

    query = 'match node where node.type=~"(?i){}" and node.pop="{}" '.format(resource_type, pop)

    for q in query_params:
        if len(q[0]) > 0 and len(q[1]) > 0:
            val = '(?i).*%s.*' % (q[1])
            query += 'and node.attributes=~"{}"'.format(val)

    query += ' return node.physical_name'

    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + graph_url)

    for record in data.records:
        if record['node.physical_name']:
            results.append(record['node.physical_name'])

    return results


def create_pop(pop_url, uuid, timestamp, properties=None):
    """
    Create a node in PoP DB representing a Point Of Presence
    :param pop_url: Url of PoP DB
    :param uuid: Uuid of the node to be created
    :param timestamp: timestamp of the creation
    :param properties: optionally dict containing key values representing
    PoP Properties
    """
    if not properties:
        properties = dict()
    properties['type'] = 'pop'
    index = ('pop', 'uuid', uuid)
    graph_db = neo4j.Graph(pop_url)
    neo_resource.add_node(graph_db, index, timestamp, properties=properties)


def update_pop(pop_url, uuid, timestamp, properties=None):
    """
    Update a node in PoP DB representing a Point Of Presence
    :param pop_url: Url of PoP DB
    :param uuid: Uuid of the node to be updated
    :param timestamp: timestamp of the update
    :param properties: optionally dict containing key values representing new
    PoP Properties
    """
    if not properties:
        properties = dict()
    properties['type'] = 'pop'
    index = ('pop', 'uuid', uuid)
    graph_db = neo4j.Graph(pop_url)
    neo_resource.update_node(graph_db, index, timestamp, properties=properties)


def add_pop_edge(pop_url, src_uuid, trg_uuid, timestamp, label, properties=None):
    """
    Add new link between two PoPs
    :param pop_url: Url of PoP DB
    :param src_uuid: Source uuid
    :param trg_uuid: Target uuid
    :param timestamp: timestamp of the update
    :param label: Label of the link
    :param properties: optionally dict containing key values representing
    PoP link Properties
    """
    if not properties:
        properties = dict()
    graph_db = neo4j.Graph(pop_url)
    src_index = ('pop', 'uuid', src_uuid)
    trg_index = ('pop', 'uuid', trg_uuid)
    db_src = neo_resource.get_node(graph_db, src_index)
    db_trg = neo_resource.get_node(graph_db, trg_index)
    properties['timestamp'] = timestamp
    edge = Relationship.cast(db_src, label, db_trg, properties)
    graph_db.create(edge)


def get_pop(pop_url, uuid):
    """
    Retrieve PoP given the uuid
    :param pop_url: Url of PoP DB
    :param uuid: PoP uuid
    :return dict: Dictionary containing PoP properties
    """
    graph_db = neo4j.Graph(pop_url)
    index = ('pop', 'uuid', uuid)
    pop = neo_resource.get_node(graph_db, index)
    if pop:
        results = dict(pop.properties)
        return results
    raise HTTPError(404, 'Resource not found: /pop/' + uuid)


def delete_pop(pop_url, uuid):
    """
    Delete PoP with given uuid
    :param pop_url: Url of PoP DB
    :param uuid: PoP uuid
    """
    graph_db = neo4j.Graph(pop_url)
    index = ('pop', 'uuid', uuid)
    neo_resource.delete_node(graph_db, index=index)


def get_pop_ids(pop_url, query_params=list()):
    """
    Retrieve list of PoPs uuids
    :param pop_url: Url of the PoP DB
    :param query_params:  optional list of (key, value)s used as query parameters
    :return list: List of PoPs uuids
    """
    query = 'match node where node.type="{}" return node'.format('pop')

    graph_db = neo4j.Graph(pop_url)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)
    results = []
    for record in data.records:
        prop = dict(record.node.properties)
        filtered = False
        for q in query_params:
            if len(q[0]) > 0 and len(q[1]) > 0:
                if q[0] == 'name' or q[0] == 'occi.epa.pop.name':
                    if prop['occi.epa.pop.name'].lower() != q[1].lower():
                        filtered = True
                else:
                    tmp = repr(prop[q[0]]).lower()
                    if tmp != q[1].lower():
                        filtered = True
        if not filtered:
            results.append(prop['uuid'])
    return results


def get_pop_links_target_uuid(pop_url, source_uuid):
    """
    Return a list of tuple containing (target uuid, target type, link uuid)
    for a given source uuid node in the PoP DB
    :param pop_url: Url of the PoP DB
    :param source_uuid: source uuid of the links to be retrieved
    :return List: List of links information
    """
    graph_db = neo4j.Graph(pop_url)
    query = 'match n-[r]->m where n.type = "pop" and n.uuid="{}" ' \
            ' return r,m'.format(source_uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)

    results = []
    for record in data.records:
        m_properties = dict(record.m.properties)
        r_properties = dict(record.r.properties)
        if 'uuid' in m_properties and 'uuid' in r_properties:
            results.append((m_properties['uuid'], m_properties['type'].lower(), r_properties['uuid']))

    return results


def get_pop_link_source_target(pop_url, uuid):
    """
    Return the source and the target uuid for a link
    specified with it uuid
    :param pop_url: Url of the PoP DB
    :param uuid: Link uuid
    :return tuple: (source uuid, target uuid)
    """
    graph_db = neo4j.Graph(pop_url)
    query = 'match n-[r]-m where r.uuid = "{}" return n.uuid, m.uuid'.format(uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)
    for record in data.records:
        return record['n.uuid'], record['m.uuid']


def get_pop_link(pop_url, uuid):
    """
    Return link properites and link label

    :param pop_url: Url of the PoP DB
    :param uuid: Link uuid
    :return tuple: (link properties, link label)
    """
    graph_db = neo4j.Graph(pop_url)
    query = 'match n-[r]-m where r.uuid = "{}" return r'.format(uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)
    for record in data.records:
        r_properties = dict(record.r.properties)
        return r_properties, record.r.type


def delete_pop_link(pop_url, uuid):
    """
    Delete link with the given uuid
    :param pop_url: Url of the PoP DB
    :param uuid: Link uuid
    """
    graph_db = neo4j.Graph(pop_url)
    query = 'match n-[r]-m where r.uuid = "{}" return r'.format(uuid)
    edge = None
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)

    for record in data.records:
        edge = record.r

    if edge:
        graph_db.delete(edge)


def _get_graph_url(pop_url, pop_id):
    """
    Retrieve EPA db url and PoP name for a given
    pop_id
    :param pop_url: Url of the PoP DB
    :param pop_id: PoP ID
    :return tuple: (EPA url, PoP name)
    """
    try:
        graph_db = neo4j.Graph(pop_url)
        index = ('pop', 'uuid', pop_id)
        pop = neo_resource.get_node(graph_db, index)
        if pop:
            properties = dict(pop.properties)
            if 'occi.epa.pop.graph_db_url' in properties and 'occi.epa.pop.name' in properties:
                return properties['occi.epa.pop.graph_db_url'], properties['occi.epa.pop.name']
    except Exception:
        raise HTTPError(404, 'Error connecting to graph_url: ' + str(pop_url))
    raise HTTPError(404, 'Resource not found: Epa-Pop-Id: ' + str(pop_id))


def get_os_dev_by_mac(pop_url, pop_id, mac):
    """
    Retrieve the osdev id with the given MAC address
    :param pop_url: Url of the PoP DB
    :param pop_id: PoP ID
    :param mac: MAC address
    :return string: osdev uuid
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)
    graph_db = neo4j.Graph(graph_url)
    query = 'match n where n.attributes=~"(?i).*{}.*" return n.physical_name'.format(mac)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)
    for record in data.records:
        return record['n.physical_name']


def get_mac_by_osdev_uuid(pop_url, pop_id, uuid):
    """
    Retrieve mac address of the osdev with the give uuid
    :param pop_url: Url of the PoP DB
    :param pop_id: PoP ID
    :param uuid: OS device uuid
    :return string: MAC address
    """
    graph_url, pop = _get_graph_url(pop_url, pop_id)
    graph_db = neo4j.Graph(graph_url)
    query = 'match n where n.physical_name="{}" return n.attributes'.format(uuid)
    try:
        data = graph_db.cypher.execute(query)
    except Exception:
        raise HTTPError(400, "Error connecting to graph url " + pop_url)
    for record in data.records:
        json_attr = json.loads(record['n.attributes'])
        return json_attr.get('Address', None)

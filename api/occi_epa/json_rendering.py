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

__author__ = 'gpetralia'

from occi.protocol.json_rendering import JsonRendering

from occi.protocol.json_rendering import _from_category
from occi.handlers import CONTENT_TYPE
import json
from occi.core_model import Resource, Link


def _epa_from_entity(entity):
    """
    Create a JSON struct for an entity.
    """


    data = {'kind': _from_category(entity.kind)}
    # kind

    #if isinstance(entity, Resource) and entity.kind != 'pop':
        #entity.identifier =


    # mixins
    mixins = []
    for mixin in entity.mixins:
        tmp = _from_category(mixin)
        mixins.append(tmp)
    data['mixins'] = mixins

    # actions
    actions = []
    for action in entity.actions:
        tmp = {'kind': _from_category(action), 'link': entity.identifier +
               '?action=' + action.term}
        actions.append(tmp)
    data['actions'] = actions

    # links
    if isinstance(entity, Resource):
        links = []
        for link in entity.links:
            tmp = _epa_from_entity(link)
            tmp['source'] = link.source.identifier
            tmp['target'] = link.target.identifier
            tmp['identifier'] = link.identifier
            links.append(tmp)
        data['links'] = links
    if isinstance(entity, Link):
        data['source'] = entity.source.identifier
        data['target'] = entity.target.identifier
    # attributes
    attr = {}
    for attribute in entity.attributes:
        attr[attribute] = entity.attributes[attribute]
    data['attributes'] = attr
    data['identifier'] = entity.identifier

    return data


class EPAJsonRendering(JsonRendering):
    """
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    """

    mime_type = 'application/occi+json'

    def from_entity(self, entity):
        data = _epa_from_entity(entity)
        body = json.dumps(data, sort_keys=True, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body

    def from_entities(self, entities, key):
        data = []
        for item in entities:
            data.append(_epa_from_entity(item))

        body = json.dumps(data, sort_keys=True, indent=2)
        return {CONTENT_TYPE: self.mime_type}, body
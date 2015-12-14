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
PoP and PoP Links Backends implementation
"""
__author__ = 'gpetralia'

from occi.backend import KindBackend, ActionBackend
from api import epa_glue
import time


class PoPBackend(KindBackend, ActionBackend):
    """
    PoP backend
    """
    def retrieve(self, entity, extras):
        """
        PoP GET Action implementation

        :param entity: Entity to be retrieved
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        uuid = entity.identifier[1:].split('/')[1]
        result = epa_glue.get_pop(extras['pop_url'], uuid)
        for key in result:
            if not key.startswith('occi.epa.pop.'):
                entity_key = 'occi.epa.pop' + key
            else:
                entity_key = key
            entity.attributes[entity_key] = result[key]

    def create(self, entity, extras):
        """
        PoP POST Action implementation

        :param entity: Entity to be created
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        now = time.time()
        uuid = entity.identifier[1:].split('/')[1]
        properties = entity.attributes
        epa_glue.create_pop(extras['pop_url'], uuid, now, properties=properties)

    def update(self, old, new, extras):
        """
        PoP PUT Action implementation
        :param old: Old entity to be updated
        :param new: New entity
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        now = time.time()
        uuid = old.identifier[1:].split('/')[1]
        properties = new.attributes
        epa_glue.update_pop(extras['pop_url'], uuid, now, properties=properties)

    def delete(self, entity, extras):
        """
        PoP DELETE action implementation
        :param entity: Entity to be deleted
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        uuid = entity.identifier[1:].split('/')[1]
        epa_glue.delete_pop(extras['pop_url'], uuid)


class PoPLinkBackend(KindBackend):
    """
    PoP Link backend
    """
    def create(self, link, extras):
        """
        PoP Link POST Action implementation

        :param link: Link to be created
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        src_uuid = link.source.identifier[1:].split('/')[1]
        trg_uuid = link.target.identifier[1:].split('/')[1]
        now = time.time()
        label = 'is_connected_to'
        uuid = link.identifier[1:].split('/')[2]
        properties = link.attributes
        properties['uuid'] = uuid
        epa_glue.add_pop_edge(extras['pop_url'], src_uuid, trg_uuid, now, label, properties=properties)

    def update(self, old, new, extras):
        """
        PoP Link PUT Action implementation

        :param old: old link to be updated
        :param new: new link
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        new.identifier = old.identifier
        uuid = old.identifier[1:].split('/')[2]
        epa_glue.delete_pop_link(extras['pop_url'], uuid)
        self.create(new, extras)

    def retrieve(self, link, extras):
        """
        PoP Link GET Action implementation
        :param link: Link to be retrieved
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        uuid = link.identifier[1:].split('/')[2]
        properties, label = epa_glue.get_pop_link(extras['pop_url'], uuid)

        for key in properties:
            if not key.startswith('occi.epa.pop.'):
                entity_key = 'occi.epa.pop.' + key
            else:
                entity_key = key
            link.attributes[entity_key] = properties[key]

        link.attributes['occi.epa.label'] = label

    def delete(self, entity, extras):
        """
        PoP Link DELETE Action implementation
        :param link: Link to be deleted
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        uuid = entity.identifier[1:].split('/')[2]
        epa_glue.delete_pop_link(extras['pop_url'], uuid)
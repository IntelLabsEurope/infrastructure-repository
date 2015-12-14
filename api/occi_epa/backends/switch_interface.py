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
Module for Physical Switch Interface OCCI backend
"""

__author__ = 'gpetralia'

from occi.backend import KindBackend, ActionBackend
from api import opendaylight_glue as odl_glue


class SwitchInterfaceBackend(KindBackend, ActionBackend):
    """
    Switch Interface backend
    """
    def retrieve(self, entity, extras):
        """
        Physical Switch Interface GET Action implementation.
        Information is retrieved using OpenDaylight API

        :param entity: Entity to be retrieved
        :param extras: Any extra arguments. It should contain at least PoP Url and PoP ID
        """
        uuid = entity.identifier[1:].split('/')[3]
        pop_id = extras['pop_id']
        result = odl_glue.get_switch_interface(extras['pop_url'], pop_id, uuid) or {}
        for key in result:
            entity.attributes['occi.epa.' + key] = result[key]
        entity.attributes['occi.epa.resource_type'] = 'physical'
        entity.attributes['occi.epa.category'] = 'network'
        entity.attributes['occi.epa.pop_id'] = pop_id


class SwitchInterfaceLinkBackend(KindBackend):
    """
    Switch Interface Link backend
    """
    def retrieve(self, link, extras):
        """
        Physical Switch Interface GET Action implementation
        :param link: Link to be retrieved
        :param extras: Any extras arguments
        """
        link.attributes['occi.epa.label'] = 'internal'

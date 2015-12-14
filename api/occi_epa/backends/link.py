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
Module for Link OCCI Backend
"""

__author__ = 'gpetralia'

from occi.backend import KindBackend
from api import epa_glue


class LinkBackend(KindBackend):
    """
    Link backend
    """
    def retrieve(self, link, extras):
        """
        Retrive the link relying on the convention that a link has ID
        source_uuid->target_uuid
        :param link: link to be retrieved
        :param extras: Any extra parameters that can be specified by the user
        """
        resource_type = link.identifier[1:].split('/')[0]
        source_uuid = link.identifier[1:].split('/')[4].split('->')[0]
        target_uuid = link.identifier[1:].split('/')[4].split('->')[1]
        pop_id = extras['pop_id']
        result = epa_glue.get_link(extras['pop_url'], pop_id, source_uuid, target_uuid)

        if resource_type == 'osdev' and 'openflow' in target_uuid:
            link.attributes['occi.epa.label'] = 'wired'
        else:
            if 'label' in result:
                link.attributes['occi.epa.label'] = result['label']
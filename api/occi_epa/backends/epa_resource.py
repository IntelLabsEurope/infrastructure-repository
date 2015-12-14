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

from occi.backend import KindBackend, ActionBackend
from api import epa_glue


class EpaResourceBackend(KindBackend, ActionBackend):
    """
    Generic Epa Resource Backend.
    It uses the name of the class to select the respective function
    from epa_glue module to retrieve information from EPA DB.
    It can't be instantiated, as its constructor is abstract.
    Backends, that implements it, should implement the constructor,
    and set a string representing the kind in the EPA DB and a boolean
    that specify if the resource is a physical resource or not.
    """

    def __init__(self):
        pass

    def retrieve(self, entity, extras):
        """
        Respond to GET call
        :param entity: Entity to be retrieved
        :param extras: Any extra arguments. It should contain at least PoP Url
        """
        uuid = entity.identifier[1:].split('/')[3]
        pop_id = extras['pop_id']
        resource = epa_glue.get_resource(extras['pop_url'], pop_id, self.type, uuid, physical=self.physical)
        for key in resource:
            entity.attributes['occi.epa.' + key] = resource[key]
        entity.attributes['occi.epa.' + 'pop_id'] = pop_id
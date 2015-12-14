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
OCCI application
"""
__author__ = 'gpetralia'

from occi import wsgi as occi_wsgi
from api.occi_epa.epa_registry import EPARegistry
from api.occi_epa.json_rendering import EPAJsonRendering
from api.occi_epa.text_occi_rendering import EPATextOcciRendering


class EPAApplication(occi_wsgi.Application):

    def __init__(self, pop_url):
        """
        Initialize the WSGI OCCI application.
        """
        super(EPAApplication, self).__init__(registry=EPARegistry())
        self.registry.set_renderer('application/occi+json', EPAJsonRendering(self.registry))
        self.registry.set_renderer('text/occi', EPATextOcciRendering(self.registry))
        self.pop_url = pop_url

    def __call__(self, environ, response):
        """
        Starts the overall OCCI part of the service, calling _call_occi.
        Before calling occi, it set up the params that sho  uld be passed
        :param environ: The WSGI environ.
        :param response: The WSGI response.
        """
        path = environ['PATH_INFO']

        if path.count('/') >= 4:
            split_path = path.split('/')
            new_path = '/' + split_path[3] + '/'
            if len(split_path) >= 5:
                for i in range(4, len(split_path)):
                    if split_path[i] != '':
                        new_path += split_path[i] + '/'

            if path[-1] != '/':
                new_path = new_path[:-1]

            environ['PATH_INFO'] = new_path
            environ['HTTP_EPA_POP_ID'] = split_path[2]

        # query parameters
        query_string = environ['QUERY_STRING']

        queries = query_string.split('&')

        extra_query = []
        for query in queries:
            if '=' in query:
                tmp = query.split('=')
                if len(tmp) > 1:
                    param = tmp[0]
                    value = tmp[1]
                    extra_query.append((param, value))

        # parsing kind from the path of the call
        kind = None

        if len(path) > 1:
            kind = environ['PATH_INFO'][1:].split('/')[0]

        # specify pop_id
        if 'HTTP_EPA_POP_ID' in environ:
            return self._call_occi(environ, response, registry=self.registry, pop_id=environ['HTTP_EPA_POP_ID'],
                                   kind=kind, query=extra_query, pop_url=self.pop_url)
        else:
            return self._call_occi(environ, response, registry=self.registry, kind=kind,
                                   query=extra_query, pop_url=self.pop_url)

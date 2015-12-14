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

from occi.protocol.occi_rendering import TextOcciRendering
from occi.protocol.occi_rendering import _extract_data_from_body, _extract_data_from_headers


class EPATextOcciRendering(TextOcciRendering):
    """
    This is a rendering which will use the HTTP header to place the information
    in an syntax and semantics as defined in the OCCI specification.
    """
    def get_data(self, headers, body):
        """
        Override the default TextOcciRendering get_data method
        to include links information in the body.

        headers -- The headers of the request.
        body -- The body of the request.
        """

        data_header = _extract_data_from_headers(headers)
        data_body = _extract_data_from_body(body)
        data_header.categories += data_body.categories
        data_header.links += data_body.links
        data_header.attributes += data_body.attributes
        data_header.locations += data_body.locations
        return data_header

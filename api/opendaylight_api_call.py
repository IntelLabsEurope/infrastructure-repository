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
Module to make a call to OpenDaylight give URL, name and password
"""

__author__ = "vmriccobene"

import pycurl
import json
from StringIO import StringIO
from occi.exceptions import HTTPError


def call_odl_api(user, password, url):
    """
    Fecth the OpenDaylight response and
    put it in a dictionary.

    :param user: OpenDaylight Username
    :param password: OpenDaylight Password
    :param url: URL OpenDaylight endpoint
    :return dict: OpenDaylight response
    """
    buf = StringIO()
    try:
        c = pycurl.Curl()
        c.setopt(pycurl.USERPWD, str(user + ':' + password))
        c.setopt(c.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Content-type: application/json"])
        c.setopt(c.WRITEDATA, buf)
        c.perform()
        c.close()
    except Exception:
        raise HTTPError(400, "Error connecting to OpenDaylight {}".format(url))
    response = ''

    for string_buf in buf.buflist:
        response += string_buf

    body_json = {}

    if response.strip() != '':
        body_json = json.loads(response)

    return body_json

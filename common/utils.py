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
Utils module for helper functions.
"""
__author__ = 'gpetralia'


def config_section_map(section, config_file):
    """
    Given a config file and a section return a
    dict containing the parameters defined in the
    given section.

    :param section: Section name
    :param config_file: Config file
    :return dict: config parameters
    """
    dict1 = {}
    options = config_file.options(section)
    for option in options:
        try:
            dict1[option] = config_file.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1
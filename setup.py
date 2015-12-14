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

'''
The setuptools script.
'''

from distutils.core import setup

setup(name='infrastructure_repo',
      version='0.1.0',
      description='Datacenter infrastructure repository',
      license='Apache License v2',
      keywords='EPA, Cloud Computing, Datacenter Software',
      url='https://github.com/IntelLabsEurope/infrastructure-repository',
      packages=['api', 'api.occi_epa',
                'api.occi_epa.backends',
                'api.occi_epa.extensions',
                'common', 'infrastructure_repository',
                'monitoring_service', 'monitoring_service.epa_database',
                'monitoring_service.epa_database.openstack'],
      install_requires=['pika', 'py2neo==2.0.7', 'pyssf', 'networkx'],
      scripts=['bin/infrastructure_repo', 'bin/infrastructure_repo_api'],
      maintainer='Giuseppe Petralia',
      maintainer_email='giuseppex.petralia@intel.com',
      classifiers=["Development Status :: 3 - Alpha",
                   "License :: OSI Approved :: Apache Software License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Internet",
                   "Topic :: Scientific/Engineering",
                   "Topic :: Software Development",
                   "Topic :: System :: Distributed Computing",
                   "Topic :: Utilities",
                   "Topic :: System"
                  ],
     )
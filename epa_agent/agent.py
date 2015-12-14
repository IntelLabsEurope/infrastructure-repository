#!/usr/bin/python

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
EPA agent
"""
__author__ = 'gpetralia'

import os
import subprocess
import getopt
import sys
import ConfigParser
import pika
import json


# Name of files created by the agent
DATA_FILES = {
    'dpdk': '_dpdk.txt',
    'hwloc': '_hwloc.xml',
    'cpu': '_cpuinfo.txt',
    'sriov': '_sriov.txt'
}


def create_dpdk_file(path, hostname):
    """
    Create file containing dpdk info

    :param path: Path where stores the file
    :param hostname: hostname of the machine where the agent is running
    """
    dpdk_file_input = '/root/programs/Pktgen-DPDK/dpdk/tools/dpdk_nic_bind.py'
    dpdk_file_output = path + '/' + hostname + DATA_FILES['dpdk']
    regex_1 = "'Network devices using DPDK-compatible driver\\n=*\\n([0-9]{4}:[0-9]{2}:[0-9]{2}.[0-9]{1}.*\\n)*'"
    regex_2 = "'^[0-9]{4}:[0-9]{2}:[0-9]{2}.[0-9]{1}'"
    if os.path.isfile(dpdk_file_input):
        command = dpdk_file_input + " --status | grep -Pzo " + regex_1 + " | " \
            "grep -Pzo " + regex_2 + " > " + dpdk_file_output

        os.system(command)


def create_hwloc_file(path, hostname):
    """
    Create file containing Hardware locality info

    :param path: Path where stores the file
    :param hostname: hostname of the machine where the agent is running
    """
    hwloc_file = path + '/' + hostname + DATA_FILES['hwloc']
    command = "hwloc-ls --of xml > " + hwloc_file
    os.system(command)


def create_cpu_file(path, hostname):
    """
    Create file containing CPUs info

    :param path: Path where stores the file
    :param hostname: hostname of the machine where the agent is running
    """
    cpuinfo_file = path + '/' + hostname + DATA_FILES['cpu']
    command = "cat /proc/cpuinfo > " + cpuinfo_file
    os.system(command)


def parse_sriov(sriov_file):
    """
    Reformat file adding for each line
    number of virtual functions for each sriov nic

    :param sriov_file: file path of the sriov file
    """
    file_sriov = open(sriov_file, 'r')
    line = file_sriov.readline()
    values = {}
    while line:
        numvfs = ''
        totalvfs = ''
        line = line.strip()
        numvfs_cmd = "cat /sys/bus/pci/devices/0000\:" + line + "/sriov_numvfs"
        proc = subprocess.Popen(numvfs_cmd, shell=True, stdout=subprocess.PIPE, )
        numvfs = str(proc.communicate()[0])[:-1]
        totalvfs_cmd = "cat /sys/bus/pci/devices/0000\:" + line + "/sriov_totalvfs"
        proc = subprocess.Popen(totalvfs_cmd, shell=True, stdout=subprocess.PIPE, )
        totalvfs = str(proc.communicate()[0])[:-1]
        values['0000:' + line] = numvfs + ' ' + totalvfs
        line = file_sriov.readline()
    file_sriov.close()

    file_sriov = open(sriov_file, 'w')
    for key in values.keys():
        file_sriov.write( key + ' ' + values[key] + '\n')

    file_sriov.close()


def create_sriov_file(path, hostname, operating_system):
    """
    Create a file containg SR-IOV info

    :param path: Path where stores the file
    :param hostname: hostname of the machine where the agent is running
    :param operating_system: operating system of the machine where the agent is running
    """
    regex_1 = "'.*Ethernet controller.*\\n.*\\n.*\\n\\tKernel modules: ixgbe'"
    regex_2 = "'^[0-9]{2}:[0-9]{2}.[0-9]{1}'"
    regex_3 = "'.*Ethernet controller.*\\n.*\\n.Kernel driver in use: ixgbe"
    sriov_file = path + '/' + hostname + DATA_FILES['sriov']
    command_deb = "lspci -knn | grep -Pzo " + regex_1 + " | grep -Pzo " + regex_2 + " > " + sriov_file
    command_redhat = "lspci -knn | grep -Pzo " + regex_3 + " | grep -Pzo " + regex_2 + " > " + sriov_file
    if 'debian' in operating_system.lower() or 'ubuntu' in operating_system.lower():
        os.system(command_deb)

    if 'redhat' in operating_system.lower() or 'fedora' in operating_system.lower():
        os.system(command_redhat)

    if os.path.isfile(sriov_file):
        parse_sriov(sriov_file)


def get_hostname():
    """
    Get hostname of the machine where the agent is running

    :return string: hostname
    """
    cmd = 'cat /etc/hostname'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, )
    hostname = str(proc.communicate()[0])[:-1]
    return hostname


def main(argv):
    """
    Check for command line arguments

    """
    configuration_file = 'agent.cfg'

    try:
        opts, args = getopt.getopt(argv,"hc:",["configFile="])
    except getopt.GetoptError:
        print 'agent.py -c <config_file>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'agent.py -c <config_file>'
            sys.exit()
        elif opt in ("-c", "--config"):
            configuration_file = arg

    if configuration_file == '':
        configuration_file = 'agent.cfg'
    return configuration_file


def send_files_to_controller(data_path, config):
    """
    Sends file to the controller

    :param data_path: where files to send are stored
    :param config: config file instance
    """
    controller = config_section_map('EpaController', config)['epa_controller_ip']
    username = config_section_map('EpaController', config)['epa_controller_username']
    priv_key = config_section_map('EpaController', config)['epa_controller_priv_key']
    controller_path = config_section_map('EpaController', config)['epa_controller_path']

    for my_file in os.listdir(data_path):
        my_file_extension = my_file.split('_')[-1]
        my_file_extension = '_' + my_file_extension
        if my_file_extension in DATA_FILES.values():
            command = 'scp -i ' + priv_key + ' ' + data_path + my_file + ' ' \
                '' + username + '@' + controller + ':' + controller_path + my_file
            os.system(command)


def config_section_map(section, config_file):
    """
    Given a config file and a section return a
    dict containing the parameters defined in the
    given section.

    :param section: Section name
    :param config_file: Config file
    :return dict: config parameters
    """
    dict1 = dict()
    options = config_file.options(section)
    for option in options:
        try:
            dict1[option] = config_file.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


if __name__ == "__main__":
    config_file = main(sys.argv[1:])
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    hostname = get_hostname()
    data_path = config_section_map('EpaAgent', config)['data_path']
    operating_system = config_section_map('EpaAgent', config)['operating_system']
    create_hwloc_file(data_path, hostname)
    create_cpu_file(data_path, hostname)
    create_sriov_file(data_path, hostname, operating_system)
    create_dpdk_file(data_path, hostname)
    send_files_to_controller(data_path, config)
    rb_usr = config_section_map('RabbitMQ', config)['rb_name']
    rb_pwd = config_section_map('RabbitMQ', config)['rb_password']
    rb_host = config_section_map('RabbitMQ', config)['rb_host']
    rb_port = config_section_map('RabbitMQ', config)['rb_port']
    agents_queue = config_section_map('RabbitMQ', config)['agents_queue']
    conn_string = 'amqp://' + \
                  rb_usr + ':' \
                  + rb_pwd + '@' \
                  + rb_host + ':' \
                  + rb_port + '/%2F'
    body = {'event_type': 'agents.new',
            'hostname': hostname,
            'data_path': config_section_map('EpaController', config)['epa_controller_path']}
    parameters = pika.URLParameters(conn_string)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_publish(exchange='',
                          routing_key=agents_queue,
                          body=json.dumps(body))
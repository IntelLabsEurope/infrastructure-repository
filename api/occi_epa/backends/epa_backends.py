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
EPA Backends
Each backend inherits from EpaResourceBackend
and specifies kind and if it is a physical resource.
"""

__author__ = 'gpetralia'

from api.occi_epa.backends.epa_resource import EpaResourceBackend


class StackBackend(EpaResourceBackend):
    def __init__(self):
        super(StackBackend, self).__init__()
        self.type = 'stack'
        self.physical = False


class BridgeBackend(EpaResourceBackend):
    def __init__(self):
        super(BridgeBackend, self).__init__()
        self.type = 'bridge'
        self.physical = True


class CacheBackend(EpaResourceBackend):
    def __init__(self):
        super(CacheBackend, self).__init__()
        self.type = 'cache'
        self.physical = True


class CinderVolumeServiceBackend(EpaResourceBackend):
    def __init__(self):
        super(CinderVolumeServiceBackend, self).__init__()
        self.type = 'cinder-volume'
        self.physical = False


class ControllerServiceBackend(EpaResourceBackend):
    def __init__(self):
        super(ControllerServiceBackend, self).__init__()
        self.type = 'controller-service'
        self.physical = False


class CoreBackend(EpaResourceBackend):
    def __init__(self):
        super(CoreBackend, self).__init__()
        self.type = 'core'
        self.physical = True


class FloatingIpBackend(EpaResourceBackend):
    def __init__(self):
        super(FloatingIpBackend, self).__init__()
        self.type = 'floatingip'
        self.physical = False


class HypervisorBackend(EpaResourceBackend):
    def __init__(self):
        super(HypervisorBackend, self).__init__()
        self.type = 'hypervisor'
        self.physical = False


class MachineBackend(EpaResourceBackend):
    def __init__(self):
        super(MachineBackend, self).__init__()
        self.type = 'machine'
        self.physical = True


class NetBackend(EpaResourceBackend):
    def __init__(self):
        super(NetBackend, self).__init__()
        self.type = 'net'
        self.physical = False


class NumaNodeBackend(EpaResourceBackend):
    def __init__(self):
        super(NumaNodeBackend, self).__init__()
        self.type = 'numanode'
        self.physical = True


class OSDevBackend(EpaResourceBackend):
    def __init__(self):
        super(OSDevBackend, self).__init__()
        self.type = 'osdev'
        self.physical = True


class PCIDevBackend(EpaResourceBackend):
    def __init__(self):
        super(PCIDevBackend, self).__init__()
        self.type = 'pcidev'
        self.physical = True


class PortBackend(EpaResourceBackend):
    def __init__(self):
        super(PortBackend, self).__init__()
        self.type = 'port'
        self.physical = False


class PUBackend(EpaResourceBackend):
    def __init__(self):
        super(PUBackend, self).__init__()
        self.type = 'pu'
        self.physical = True


class RouterBackend(EpaResourceBackend):
    def __init__(self):
        super(RouterBackend, self).__init__()
        self.type = 'router'
        self.physical = False


class SnapshotBackend(EpaResourceBackend):
    def __init__(self):
        super(SnapshotBackend, self).__init__()
        self.type = 'snapshot'
        self.physical = False


class SocketBackend(EpaResourceBackend):
    def __init__(self):
        super(SocketBackend, self).__init__()
        self.type = 'socket'
        self.physical = True


class VMBackend(EpaResourceBackend):
    def __init__(self):
        super(VMBackend, self).__init__()
        self.type = 'vm'
        self.physical = False


class VolumeBackend(EpaResourceBackend):
    def __init__(self):
        super(VolumeBackend, self).__init__()
        self.type = 'volume'
        self.physical = False

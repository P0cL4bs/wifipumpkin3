from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.utility.component import ControllerBlueprint
from wifipumpkin3.core.servers.dhcp import *

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class DHCPController(ControllerBlueprint):
    ID = "dhcp_controller"

    @staticmethod
    def getID():
        return DHCPController.ID

    def __init__(self, parent):
        super(DHCPController, self).__init__()
        self.parent = parent
        # append controller in DefaultWidget
        self.parent.getDefault.addController(self)
        __dhcpmode = dhcp.DHCPSettings.instances[0].dhmode
        self.mode = {}
        for k in __dhcpmode:
            self.mode[k.ID] = k

    def Start(self):
        self.Active.Start()

    @property
    def ActiveService(self):
        return self.Active.service

    @property
    def Active(self):
        for i in self.mode.values():
            if i.isChecked():
                return i

    @property
    def ActiveReactor(self):
        # reactor=[self.Active.reactor,self.Active.service]
        return self.Active.reactor

    def Stop(self):
        self.Active.Stop()

    def getReactorInfo(self):
        info_reactor = {}
        info_reactor[self.ActiveReactor.getID()] = {
            "ID": self.ActiveReactor.getID(),
            "PID": self.ActiveReactor.getpid(),
        }
        return info_reactor

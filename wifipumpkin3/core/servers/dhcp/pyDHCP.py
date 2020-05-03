from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.packets.dhcpserver import DHCPThread
from wifipumpkin3.core.servers.dhcp.dhcp import DHCPServers
from wifipumpkin3.core.utility.printer import display_messages, setcolor

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


class PyDHCP(DHCPServers):
    Name = "Python DHCP Server"
    ID = "pydhcp_server"
    LogFile = C.LOG_PYDHCPSERVER

    def __init__(self, parent=0):
        super(PyDHCP, self).__init__(parent)
        self._isRunning = False
        self._connected = {}

    def Initialize(self):
        self.ifaceHostapd = self.conf.get("accesspoint", "interface")

    def setIsRunning(self, value):
        self._isRunning = value

    @property
    def getStatusReactor(self):
        return self._isRunning

    def get_DHCPoutPut(self, data):
        self._connected[data["MAC"]] = data
        if self.conf.get("accesspoint", "status_ap", format=bool):
            print(
                display_messages(
                    "{} client join the AP ".format(
                        setcolor(data["MAC"], color="green")
                    ),
                    info=True,
                )
            )

    def boot(self):
        self.reactor = DHCPThread(self.ifaceHostapd, self.DHCPConf)
        self.reactor.DHCPProtocol._request.connect(self.get_DHCPoutPut)
        self.reactor.send_output.connect(self.LogOutput)
        self.reactor.setObjectName(self.ID)

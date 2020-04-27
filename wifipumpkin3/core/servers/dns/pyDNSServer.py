from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.servers.dns.DNSBase import DNSBase
from wifipumpkin3.core.packets.dnsserver import DNSServerThread

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


class PyDNSServer(DNSBase):
    ID = "pydns_server"
    Name = "PyDNS Server"
    Author = "Samuel Colvin @samuelcolvin"
    LogFile = C.LOG_PYDNSSERVER
    ExecutableFile = ""

    def __init__(self, parent):
        super(PyDNSServer, self).__init__(parent)

    @property
    def commandargs(self):
        pass

    def LogOutput(self, data):
        if self.conf.get("accesspoint", "status_ap", format=bool):
            self.logger.info(data)

    def boot(self):
        self.interfaces = Refactor.get_interfaces()
        # filter dns server for only run when is connected on internet
        if self.interfaces.get("activated")[0] != None:
            self.reactor = DNSServerThread(self.conf)
            self.reactor.sendRequests.connect(self.LogOutput)
            self.reactor.setObjectName(self.ID)
